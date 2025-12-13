import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from .downloaders import ChromeDownloader, EdgeDownloader, FirefoxDownloader
from .inspector import ExtensionInspector
from .batch import BatchProcessor
from .utils import open_extension_archive, verify_file_hash, check_disk_space
from .console import console, print_manifest_table, print_search_results_table
from .preview import build_file_tree
from .auditor import ExtensionAuditor
from .diff import ExtensionDiffer
from .risk import RiskAnalyzer
from .verifier import CrxVerifier
from .hooks import HookManager, HookContext
from .config import get_config_path, load_config
from .history import HistoryManager
from .exceptions import ExtensionError, ConfigError, IntegrityError

logger = logging.getLogger(__name__)

def get_downloader(browser):
    """Factory to get the appropriate downloader instance."""
    if browser in ["chrome", "c"]:
        return ChromeDownloader()
    elif browser in ["edge", "e"]:
        return EdgeDownloader()
    elif browser in ["firefox", "f"]:
        return FirefoxDownloader()
    return None

def download_extension(browser, url, output_dir, save_metadata=False, extract=False, show_progress=True, verify_hash=None):
    """
    Download an extension from a web store.
    """
    downloader = get_downloader(browser)
    if not downloader:
        raise ConfigError(f"Unsupported browser type: {browser}")

    extension_id = downloader.extract_id(url)
    if show_progress:
        logger.info(f"Extracted ID/Slug: {extension_id}")

    # Initialize hooks
    config_dir = get_config_path().parent
    hooks_dir = config_dir / "hooks"
    hook_manager = HookManager(hooks_dir)
    
    # Load config for hooks
    try:
        config = load_config()
    except Exception:
        config = {}

    # Run pre-download hook
    ctx = HookContext(extension_id=extension_id, browser=browser, config=config)
    hook_manager.run_hook("pre_download", ctx)
    
    if ctx.cancel:
        logger.info("Download cancelled by pre_download hook.")
        return None

    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    output_path = downloader.download(extension_id, output_dir, show_progress=show_progress)
    
    # Verify hash if requested
    if verify_hash:
        if show_progress:
            logger.info(f"Verifying SHA256 hash: {verify_hash}")
        try:
            verify_file_hash(output_path, verify_hash)
            if show_progress:
                logger.info("Hash verification successful.")
        except IntegrityError as e:
            logger.error(f"Integrity check failed: {e}")
            # Cleanup
            if output_path.exists():
                output_path.unlink()
            raise

    # Update context with result
    ctx.file_path = output_path

    if save_metadata:
        if show_progress:
            logger.info("Generating metadata sidecar...")
        try:
            inspector = ExtensionInspector()
            manifest = inspector.get_manifest(output_path)
            
            metadata = {
                "id": extension_id,
                "name": manifest.get("name", "Unknown"),
                "version": manifest.get("version", "Unknown"),
                "source_url": url,
                "download_timestamp": datetime.now(timezone.utc).isoformat(),
                "filename": output_path.name
            }
            
            # Add metadata to hook context
            ctx.metadata = metadata
            
            # Save as <filename>.json (e.g. extension.crx.json)
            metadata_path = output_path.with_suffix(output_path.suffix + ".json")
            
            with metadata_path.open("w") as f:
                json.dump(metadata, f, indent=2)
                
            if show_progress:
                logger.info(f"Metadata saved to {metadata_path}")
        except Exception as e:
            logger.warning(f"Failed to generate metadata: {e}")

    # Run post-download hook
    hook_manager.run_hook("post_download", ctx)

    # Log to history
    try:
        history = HistoryManager()
        version = None
        if save_metadata and 'metadata' in locals():
            version = metadata.get("version")
        
        history.add_entry(
            action="download",
            extension_id=extension_id,
            browser=browser,
            version=version,
            status="success",
            path=str(output_path)
        )
    except Exception as e:
        logger.warning(f"Failed to update history: {e}")

    if extract:
        extract_extension(output_path, output_dir / output_path.stem, show_progress=show_progress)

    return output_path

def search_extension(browser, query, json_output=False, csv_output=False):
    """
    Search for an extension.
    """
    downloader = get_downloader(browser)
    if not downloader:
        raise ConfigError(f"Unsupported browser type: {browser}")
        
    if not hasattr(downloader, 'search'):
         raise ConfigError(f"Search not supported for {browser}")
    
    results = downloader.search(query)
    
    if json_output:
        console.print_json(data=results)
    elif csv_output:
        import csv
        import sys
        
        writer = csv.writer(sys.stdout)
        writer.writerow(["id", "name", "version", "url", "description", "users", "rating"])
        
        for r in results:
            writer.writerow([
                r.get("id", ""),
                r.get("name", ""),
                r.get("version", ""),
                r.get("url", ""),
                r.get("description", ""),
                r.get("users", ""),
                r.get("rating", "")
            ])
    else:
        print_search_results_table(query, results)
    
    return results

def inspect_extension(file_path, show_progress=True, json_output=False):
    """
    Inspect an extension file.
    """
    inspector = ExtensionInspector()
    manifest = inspector.get_manifest(file_path)
    
    if json_output:
        console.print_json(data=manifest)
    else:
        print_manifest_table(manifest)
        if show_progress:
            logger.info("Inspection finished successfully.")
    
    return manifest

def check_update(file_path, json_output=False):
    """
    Check if an extension file has an update available.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise ExtensionError(f"File not found: {file_path}")

    inspector = ExtensionInspector()
    manifest = inspector.get_manifest(file_path)
    
    local_version = manifest.get("version")
    name = manifest.get("name", "Unknown")
    
    # Try to infer ID and browser from metadata sidecar if it exists
    metadata_path = file_path.with_suffix(file_path.suffix + ".json")
    extension_id = None
    browser = None
    
    if metadata_path.exists():
        try:
            with metadata_path.open("r") as f:
                metadata = json.load(f)
                extension_id = metadata.get("id")
                source_url = metadata.get("source_url", "")
                browser = metadata.get("browser") # Trust metadata if present
                
                if not browser:
                    if "chrome.google.com" in source_url or "chromewebstore.google.com" in source_url:
                        browser = "chrome"
                    elif "microsoftedge.microsoft.com" in source_url:
                        browser = "edge"
                    elif "addons.mozilla.org" in source_url:
                        browser = "firefox"
        except Exception:
            pass
            
    # Fallback: Try to infer from update_url in manifest (Chrome/Edge)
    if not extension_id:
        update_url = manifest.get("update_url", "")
        if "clients2.google.com" in update_url:
            # This is generic for Chrome extensions, but doesn't give us the ID directly usually
            # unless we parse the key, which is hard.
            # However, if the filename is the ID (common pattern), use that.
            if len(file_path.stem) == 32:
                extension_id = file_path.stem
                browser = "chrome"
        elif "edge.microsoft.com" in update_url:
             if len(file_path.stem) == 32:
                extension_id = file_path.stem
                browser = "edge"
    
    # Fallback: Firefox ID is often in browser_specific_settings
    if not extension_id:
        bss = manifest.get("browser_specific_settings", {}).get("gecko", {})
        if "id" in bss:
            extension_id = bss["id"]
            browser = "firefox"

    if not extension_id or not browser:
        # Last ditch: check filename for 32-char ID
        if len(file_path.stem) == 32:
             # Ambiguous between Chrome and Edge, default to Chrome?
             extension_id = file_path.stem
             browser = "chrome" # Best guess
        else:
             raise ValueError("Could not determine extension ID or source browser. Please ensure metadata sidecar exists.")

    downloader = get_downloader(browser)
    remote_version = downloader.get_latest_version(extension_id)
    
    result = {
        "name": name,
        "id": extension_id,
        "browser": browser,
        "local_version": local_version,
        "remote_version": remote_version,
        "update_available": False,
        "status": "unknown"
    }
    
    if remote_version:
        # Simple string comparison might fail for semver (1.10 < 1.2), but let's assume standard versioning
        # Better to use packaging.version
        try:
            from packaging import version
            v_local = version.parse(local_version)
            v_remote = version.parse(remote_version)
            if v_remote > v_local:
                result["update_available"] = True
                result["status"] = "update_available"
            elif v_remote == v_local:
                result["status"] = "up_to_date"
            else:
                result["status"] = "local_is_newer"
        except ImportError:
            # Fallback to string comparison if packaging not available (though it should be in env)
             if remote_version != local_version:
                 result["update_available"] = True # Naive
                 result["status"] = "update_available" # Naive
    else:
        result["status"] = "check_failed"

    if json_output:
        console.print_json(data=result)
    else:
        # Print human readable
        if result["status"] == "update_available":
            console.print(f"[bold green]Update Available![/bold green] {name} ({local_version} -> {remote_version})")
        elif result["status"] == "up_to_date":
            console.print(f"[bold blue]Up to date.[/bold blue] {name} ({local_version})")
        elif result["status"] == "check_failed":
            console.print(f"[bold red]Failed to check for updates.[/bold red] {name}")
        else:
             console.print(f"[yellow]Status: {result['status']}[/yellow] {name} ({local_version} vs {remote_version})")

    return result

def preview_extension(file_path):
    """
    Preview the contents of an extension archive without extracting.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise ExtensionError(f"File not found: {file_path}")

    try:
        with open_extension_archive(file_path) as zf:
            file_list = zf.namelist()
            
        tree = build_file_tree(file_list, file_path.name)
        console.print(tree)
        
    except Exception as e:
        logger.error(f"Preview failed: {e}")
        raise ExtensionError(f"Preview failed: {e}", original_exception=e)

def audit_extension(file_path, json_output=False):
    """
    Audit an extension for MV3 compatibility.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise ExtensionError(f"File not found: {file_path}")

    auditor = ExtensionAuditor()
    try:
        report = auditor.audit(file_path)
        
        if json_output:
            # Convert dataclass to dict
            from dataclasses import asdict
            console.print_json(data=asdict(report))
        else:
            # Print report
            console.print(f"[bold]Manifest Version:[/bold] {report.manifest_version}")
            if report.is_mv3:
                console.print("[bold green]MV3 Compatible[/bold green]")
            else:
                console.print("[bold yellow]MV2 Legacy[/bold yellow]")
                
            if report.issues:
                console.print("\n[bold]Issues:[/bold]")
                for issue in report.issues:
                    color = "red" if issue.severity == "error" else "yellow" if issue.severity == "warning" else "blue"
                    loc = f"{issue.file}"
                    if issue.line:
                        loc += f":{issue.line}"
                    console.print(f"[{color}]• {issue.message}[/{color}] ([dim]{loc}[/dim])")
            else:
                console.print("\n[bold green]No issues found.[/bold green]")
                
        return report
    except Exception as e:
        logger.error(f"Audit failed: {e}")
        raise

def diff_extensions(old_path, new_path, json_output=False, ignore_whitespace=False):
    """
    Compare two extension archives.
    """
    old_path = Path(old_path)
    new_path = Path(new_path)
    
    if not old_path.exists():
        raise ExtensionError(f"File not found: {old_path}")
    if not new_path.exists():
        raise ExtensionError(f"File not found: {new_path}")

    differ = ExtensionDiffer()
    try:
        report = differ.diff(old_path, new_path, ignore_whitespace=ignore_whitespace)
        
        if json_output:
            from dataclasses import asdict
            console.print_json(data=asdict(report))
        else:
            console.print("[bold]Diff Report[/bold]")
            console.print(f"Old Version: {report.old_version} -> New Version: {report.new_version}")
            
            if report.manifest_changes:
                console.print("\n[bold]Manifest Changes:[/bold]")
                for key, (old, new) in report.manifest_changes.items():
                    console.print(f"  [yellow]{key}[/yellow]: {old} -> {new}")
            
            if report.added_files:
                console.print(f"\n[bold green]Added Files ({len(report.added_files)}):[/bold green]")
                for f in report.added_files[:10]:
                    console.print(f"  + {f}")
                if len(report.added_files) > 10:
                    console.print(f"  ... and {len(report.added_files) - 10} more")
                    
            if report.removed_files:
                console.print(f"\n[bold red]Removed Files ({len(report.removed_files)}):[/bold red]")
                for f in report.removed_files[:10]:
                    console.print(f"  - {f}")
                if len(report.removed_files) > 10:
                    console.print(f"  ... and {len(report.removed_files) - 10} more")
                    
            if report.modified_files:
                console.print(f"\n[bold blue]Modified Files ({len(report.modified_files)}):[/bold blue]")
                for f in report.modified_files[:10]:
                    console.print(f"  ~ {f}")
                if len(report.modified_files) > 10:
                    console.print(f"  ... and {len(report.modified_files) - 10} more")

            if report.image_changes:
                console.print(f"\n[bold magenta]Image Changes ({len(report.image_changes)}):[/bold magenta]")
                for img in report.image_changes:
                    console.print(f"  * {img['file']}: {img['diff']}")
                    
        return report
    except Exception as e:
        logger.error(f"Diff failed: {e}")
        raise

def analyze_risk(file_path, json_output=False):
    """
    Analyze the privacy risk of an extension.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise ExtensionError(f"File not found: {file_path}")

    analyzer = RiskAnalyzer()
    try:
        report = analyzer.analyze(file_path)
        
        if json_output:
            from dataclasses import asdict
            console.print_json(data=asdict(report))
        else:
            # Color code the max level
            level_color = {
                "Critical": "red",
                "High": "orange1",
                "Medium": "yellow",
                "Low": "blue",
                "Safe": "green"
            }.get(report.max_level, "white")
            
            console.print("[bold]Risk Analysis Report[/bold]")
            console.print(f"Overall Risk Level: [{level_color} bold]{report.max_level}[/{level_color} bold]")
            console.print(f"Total Risk Score: {report.total_score}")
            
            if report.risky_permissions:
                console.print("\n[bold]Risky Permissions:[/bold]")
                for p in report.risky_permissions:
                    p_color = {
                        "Critical": "red",
                        "High": "orange1",
                        "Medium": "yellow",
                        "Low": "blue"
                    }.get(p.level, "white")
                    console.print(f"  [{p_color}]• {p.permission}[/{p_color}] (Score: {p.score}) - [dim]{p.description}[/dim]")
            
            if report.safe_permissions:
                console.print(f"\n[bold green]Safe/Unknown Permissions ({len(report.safe_permissions)}):[/bold green]")
                console.print(f"  {', '.join(report.safe_permissions)}")
                
        return report
    except Exception as e:
        logger.error(f"Risk analysis failed: {e}")
        raise

def verify_signature(file_path, json_output=False):
    """
    Verify the cryptographic signature of a CRX file.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise ExtensionError(f"File not found: {file_path}")
        
    verifier = CrxVerifier()
    try:
        is_valid = verifier.verify(file_path)
        
        result = {
            "file": str(file_path),
            "verified": is_valid,
            "algorithm": "RSA-SHA256"
        }
        
        if json_output:
            console.print_json(data=result)
        else:
            if is_valid:
                console.print("[bold green]Signature Verified[/bold green] (RSA-SHA256)")
            else:
                console.print("[bold red]Verification Failed[/bold red]")
                
        return is_valid
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        if json_output:
             console.print_json(data={"file": str(file_path), "verified": False, "error": str(e)})
        else:
             console.print(f"[bold red]Verification Error:[/bold red] {e}")
        return False

def extract_extension(file_path, output_dir=None, show_progress=True):
    """
    Extract an extension archive.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise ExtensionError(f"File not found: {file_path}")
    
    if output_dir:
        extract_dir = Path(output_dir)
    else:
        extract_dir = Path(".") / file_path.stem
        
    if extract_dir.exists() and any(extract_dir.iterdir()):
         logger.warning(f"Extraction directory {extract_dir} is not empty.")
    
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    if show_progress:
        logger.info(f"Extracting {file_path} to {extract_dir}...")
    
    try:
        with open_extension_archive(file_path) as zf:
            # Check disk space
            total_size = sum(info.file_size for info in zf.infolist())
            check_disk_space(extract_dir, total_size)
            
            zf.extractall(extract_dir)
        if show_progress:
            logger.info(f"Successfully extracted to {extract_dir}")

        # Run post-extract hook
        try:
            config_dir = get_config_path().parent
            hooks_dir = config_dir / "hooks"
            hook_manager = HookManager(hooks_dir)
            try:
                config = load_config()
            except Exception:
                config = {}
            
            # Try to infer ID/browser for context
            extension_id = "unknown"
            browser = "unknown"
            metadata_path = file_path.with_suffix(file_path.suffix + ".json")
            if metadata_path.exists():
                try:
                    with metadata_path.open("r") as f:
                        meta = json.load(f)
                        extension_id = meta.get("id", "unknown")
                        source_url = meta.get("source_url", "")
                        if "google.com" in source_url:
                            browser = "chrome"
                        elif "microsoft.com" in source_url:
                            browser = "edge"
                        elif "mozilla.org" in source_url:
                            browser = "firefox"
                except Exception:
                    pass

            ctx = HookContext(
                extension_id=extension_id, 
                browser=browser, 
                file_path=extract_dir,
                config=config
            )
            hook_manager.run_hook("post_extract", ctx)
        except Exception as e:
            logger.warning(f"Failed to run post-extract hook: {e}")

        # Log to history
        try:
            # Try to find metadata sidecar
            metadata_path = file_path.with_suffix(file_path.suffix + ".json")
            extension_id = "unknown"
            browser = "unknown"
            version = None
            
            if metadata_path.exists():
                with metadata_path.open("r") as f:
                    meta = json.load(f)
                    extension_id = meta.get("id", "unknown")
                    source_url = meta.get("source_url", "")
                    if "google.com" in source_url:
                        browser = "chrome"
                    elif "microsoft.com" in source_url:
                        browser = "edge"
                    elif "mozilla.org" in source_url:
                        browser = "firefox"
                    version = meta.get("version")
            
            HistoryManager().add_entry(
                action="extract",
                extension_id=extension_id,
                browser=browser,
                version=version,
                status="success",
                path=str(extract_dir)
            )
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise ExtensionError(f"Extraction failed: {e}", original_exception=e)

def batch_download(file_path, output_dir, workers=4, show_progress=True):
    """
    Process a batch file of extension URLs.
    """
    processor = BatchProcessor()
    processor.process(file_path, output_dir, max_workers=workers, show_progress=show_progress)
    if show_progress:
        logger.info("Batch processing finished successfully.")

def scan_extension(file_path, json_output=False, csv_output=False):
    """
    Scan an extension for vulnerable dependencies.
    """
    from .scanner import DependencyScanner
    from dataclasses import asdict
    
    file_path = Path(file_path)
    if not file_path.exists():
        raise ExtensionError(f"File not found: {file_path}")

    scanner = DependencyScanner()
    try:
        report = scanner.scan(file_path)
        
        if json_output:
            console.print_json(data=asdict(report))
        elif csv_output:
            import csv
            import sys
            
            writer = csv.writer(sys.stdout)
            writer.writerow(["file", "library", "version", "vulnerable", "advisory", "path"])
            
            if report.libraries:
                for lib in report.libraries:
                    writer.writerow([
                        report.file,
                        lib.name,
                        lib.version,
                        lib.vulnerable,
                        lib.advisory,
                        lib.path
                    ])
        else:
            console.print(f"[bold]Dependency Scan Report:[/bold] {report.file}")
            if not report.libraries:
                console.print("[green]No known libraries detected.[/green]")
            else:
                for lib in report.libraries:
                    status = "[red]VULNERABLE[/red]" if lib.vulnerable else "[green]OK[/green]"
                    console.print(f"  • [bold]{lib.name}[/bold] v{lib.version} ({status})")
                    console.print(f"    Path: [dim]{lib.path}[/dim]")
                    if lib.vulnerable:
                        console.print(f"    Advisory: [red]{lib.advisory}[/red]")
                        
        return report
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise

def generate_report(file_path, output_path=None):
    """
    Generate a Markdown report for an extension.
    """
    from .reporter import MarkdownReporter
    
    file_path = Path(file_path)
    if not file_path.exists():
        raise ExtensionError(f"File not found: {file_path}")

    reporter = MarkdownReporter(file_path)
    try:
        if output_path:
            output_path = Path(output_path)
        else:
            # Default to <filename>_REPORT.md
            output_path = Path(f"{file_path.name}_REPORT.md")
            
        reporter.save(output_path)
        logger.info(f"Report saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise ExtensionError(f"Report generation failed: {e}", original_exception=e)

def convert_extension(input_path, output_path=None, to_format="zip"):
    """
    Convert extension format.
    """
    from .converter import FormatConverter
    
    if to_format.lower() != "zip":
        raise ConfigError(f"Unsupported target format: {to_format}. Only 'zip' is supported currently.")
        
    try:
        return FormatConverter.convert_to_zip(input_path, output_path)
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise ExtensionError(f"Conversion failed: {e}", original_exception=e)

def get_repo_stats(directory, json_output=False):
    """
    Analyze a repository of extensions.
    """
    from .stats import RepoAnalyzer, print_stats
    from dataclasses import asdict
    
    directory = Path(directory)
    if not directory.exists():
        raise ConfigError(f"Directory not found: {directory}")
        
    analyzer = RepoAnalyzer()
    stats = analyzer.scan(directory)
    
    if json_output:
        console.print_json(data=asdict(stats))
    else:
        print_stats(stats)
        
    return stats

def generate_unified_report(file_path, yara_rules=None):
    """
    Generate a comprehensive unified report for an extension.
    """
    from .inspector import ExtensionInspector
    from .risk import RiskAnalyzer
    from .auditor import ExtensionAuditor
    from .analysis.complexity import analyze_complexity
    from .analysis.entropy import analyze_entropy
    from .analysis.domains import analyze_domains
    from .secrets import SecretScanner
    from .analysis.yara import YaraScanner
    from dataclasses import asdict
    import hashlib

    file_path = Path(file_path)
    if not file_path.exists():
        raise ExtensionError(f"File not found: {file_path}")

    # Initialize hooks
    config_dir = get_config_path().parent
    hooks_dir = config_dir / "hooks"
    hook_manager = HookManager(hooks_dir)
    try:
        config = load_config()
    except Exception:
        config = {}

    # Run pre-analysis hook
    ctx = HookContext(extension_id=file_path.stem, browser="unknown", file_path=file_path, config=config)
    hook_manager.run_hook("pre_analysis", ctx)
    
    if ctx.cancel:
        logger.info("Analysis cancelled by pre_analysis hook.")
        return {}

    report = {}

    # 1. Metadata
    inspector = ExtensionInspector()
    manifest = inspector.get_manifest(file_path)
    
    # Calculate hashes
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        sha256.update(f.read())
    
    report["metadata"] = {
        "filename": file_path.name,
        "size": file_path.stat().st_size,
        "sha256": sha256.hexdigest(),
        "manifest": manifest
    }

    # 2. MV3 Audit
    auditor = ExtensionAuditor()
    mv3_report = auditor.audit(file_path)
    report["mv3_audit"] = asdict(mv3_report)

    # 3. Risk Analysis
    risk_analyzer = RiskAnalyzer()
    risk_report = risk_analyzer.analyze(file_path)
    report["risk_analysis"] = asdict(risk_report)

    # 4. Complexity
    report["complexity"] = analyze_complexity(file_path)

    # 5. Entropy
    report["entropy"] = analyze_entropy(file_path)

    # 6. Domains
    domain_report = analyze_domains(file_path)
    report["domains"] = domain_report["domains"]
    report["urls"] = domain_report["urls"]

    # 7. Secrets
    secret_scanner = SecretScanner()
    secrets = secret_scanner.scan_extension(file_path)
    report["secrets"] = [asdict(s) for s in secrets]

    # 8. YARA (Optional)
    if yara_rules:
        try:
            yara_scanner = YaraScanner(yara_rules)
            report["yara_matches"] = yara_scanner.scan_archive(file_path)
        except Exception as e:
            logger.warning(f"YARA scan failed: {e}")
            report["yara_matches"] = {"error": str(e)}
    else:
        report["yara_matches"] = None

    # Run post-analysis hook
    ctx.result = report
    hook_manager.run_hook("post_analysis", ctx)
    
    # Allow hook to modify report
    if ctx.result:
        report = ctx.result

    return report

def generate_html_report(file_path, output_path=None, yara_rules=None):
    """
    Generate an HTML report for an extension.
    """
    from .reporter import HtmlReporter
    
    file_path = Path(file_path)
    if not file_path.exists():
        raise ExtensionError(f"File not found: {file_path}")

    # Get unified data
    data = generate_unified_report(file_path, yara_rules=yara_rules)
    
    reporter = HtmlReporter(data)
    try:
        if output_path:
            output_path = Path(output_path)
        else:
            output_path = Path(f"{file_path.name}_REPORT.html")
            
        reporter.save(output_path)
        logger.info(f"HTML Report saved to {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"HTML Report generation failed: {e}")
        raise ExtensionError(f"HTML Report generation failed: {e}", original_exception=e)

