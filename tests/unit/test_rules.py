from fetchext.analysis.rules import RuleEngine

def test_rule_engine_load(tmp_path):
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("""
rules:
  - id: test-rule
    description: Test Rule
    severity: high
    pattern: "test"
""")
    
    engine = RuleEngine(rules_file)
    assert len(engine.rules) == 1
    assert engine.rules[0]["id"] == "test-rule"

def test_rule_engine_scan(tmp_path):
    rules_file = tmp_path / "rules.yaml"
    rules_file.write_text("""
rules:
  - id: test-rule
    pattern: "secret"
""")
    
    engine = RuleEngine(rules_file)
    
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    target_file = target_dir / "target.txt"
    target_file.write_text("this is a secret message")
    
    matches = engine.scan(target_dir) # Scan directory
    
    assert len(matches) == 1
    assert matches[0].rule_id == "test-rule"
    assert matches[0].match == "this is a secret message"
