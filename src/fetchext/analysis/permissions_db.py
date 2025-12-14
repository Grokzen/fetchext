PERMISSIONS_DB = {
    "activeTab": {
        "description": "Grants temporary access to the currently active tab when the user invokes the extension (e.g., by clicking its icon).",
        "risk": "Low",
    },
    "alarms": {
        "description": "Grants access to the chrome.alarms API to schedule code to run periodically or at a specified time.",
        "risk": "Low",
    },
    "background": {
        "description": "Allows the extension to run in the background, even when no browser windows are open.",
        "risk": "Medium",
    },
    "bookmarks": {
        "description": "Grants access to the chrome.bookmarks API to create, organize, and manipulate bookmarks.",
        "risk": "Medium",
    },
    "browsingData": {
        "description": "Grants access to the chrome.browsingData API to clear browsing data (history, cookies, cache, etc.).",
        "risk": "High",
    },
    "clipboardRead": {
        "description": "Allows the extension to read data from the clipboard using the Clipboard API.",
        "risk": "High",
    },
    "clipboardWrite": {
        "description": "Allows the extension to write data to the clipboard.",
        "risk": "Low",
    },
    "contentSettings": {
        "description": "Grants access to the chrome.contentSettings API to change browser settings like cookie handling, javascript execution, etc.",
        "risk": "High",
    },
    "contextMenus": {
        "description": "Grants access to the chrome.contextMenus API to add items to the browser's context menu.",
        "risk": "Low",
    },
    "cookies": {
        "description": "Grants access to the chrome.cookies API to query and modify cookies.",
        "risk": "High",
    },
    "debugger": {
        "description": "Grants access to the chrome.debugger API, allowing the extension to use the Chrome DevTools Protocol to inspect and control the browser.",
        "risk": "Critical",
    },
    "declarativeNetRequest": {
        "description": "Grants access to the chrome.declarativeNetRequest API to block or modify network requests in a privacy-preserving way.",
        "risk": "Medium",
    },
    "declarativeNetRequestFeedback": {
        "description": "Grants access to information about which rules matched in declarativeNetRequest.",
        "risk": "High",
    },
    "desktopCapture": {
        "description": "Grants access to the chrome.desktopCapture API to capture screen content.",
        "risk": "High",
    },
    "downloads": {
        "description": "Grants access to the chrome.downloads API to manage downloads.",
        "risk": "Medium",
    },
    "downloads.open": {
        "description": "Allows the extension to open downloaded files.",
        "risk": "High",
    },
    "geolocation": {
        "description": "Allows the extension to access the user's physical location.",
        "risk": "High",
    },
    "history": {
        "description": "Grants access to the chrome.history API to read and write to the browser history.",
        "risk": "High",
    },
    "identity": {
        "description": "Grants access to the chrome.identity API to get OAuth2 access tokens.",
        "risk": "Medium",
    },
    "idle": {
        "description": "Grants access to the chrome.idle API to detect when the machine's idle state changes.",
        "risk": "Low",
    },
    "management": {
        "description": "Grants access to the chrome.management API to manage installed extensions and apps.",
        "risk": "High",
    },
    "nativeMessaging": {
        "description": "Allows the extension to exchange messages with a native application installed on the user's computer.",
        "risk": "High",
    },
    "notifications": {
        "description": "Grants access to the chrome.notifications API to create rich notifications.",
        "risk": "Low",
    },
    "pageCapture": {
        "description": "Grants access to the chrome.pageCapture API to save a tab as MHTML.",
        "risk": "Medium",
    },
    "power": {
        "description": "Grants access to the chrome.power API to override the system's power management features.",
        "risk": "Low",
    },
    "printerProvider": {
        "description": "Grants access to the chrome.printerProvider API to implement a print manager.",
        "risk": "Medium",
    },
    "privacy": {
        "description": "Grants access to the chrome.privacy API to control privacy-related settings.",
        "risk": "High",
    },
    "proxy": {
        "description": "Grants access to the chrome.proxy API to manage the browser's proxy settings.",
        "risk": "High",
    },
    "scripting": {
        "description": "Grants access to the chrome.scripting API to execute scripts in different contexts.",
        "risk": "High",
    },
    "search": {
        "description": "Grants access to the chrome.search API to search via the default provider.",
        "risk": "Low",
    },
    "sessions": {
        "description": "Grants access to the chrome.sessions API to query and restore tabs and windows from a browsing session.",
        "risk": "Medium",
    },
    "storage": {
        "description": "Grants access to the chrome.storage API to store, retrieve, and track changes to user data.",
        "risk": "Low",
    },
    "system.cpu": {
        "description": "Grants access to the chrome.system.cpu API to query CPU metadata.",
        "risk": "Low",
    },
    "system.memory": {
        "description": "Grants access to the chrome.system.memory API to query memory metadata.",
        "risk": "Low",
    },
    "system.storage": {
        "description": "Grants access to the chrome.system.storage API to query storage device information.",
        "risk": "Low",
    },
    "tabCapture": {
        "description": "Grants access to the chrome.tabCapture API to capture the visible area of the active tab.",
        "risk": "High",
    },
    "tabs": {
        "description": "Grants access to the chrome.tabs API to interact with the browser's tab system (create, modify, rearrange tabs). Note: Often grants access to URL and title of tabs.",
        "risk": "High",
    },
    "topSites": {
        "description": "Grants access to the chrome.topSites API to access the top sites (most visited) list.",
        "risk": "Medium",
    },
    "tts": {
        "description": "Grants access to the chrome.tts API to play synthesized text-to-speech.",
        "risk": "Low",
    },
    "ttsEngine": {
        "description": "Grants access to the chrome.ttsEngine API to implement a text-to-speech engine.",
        "risk": "Medium",
    },
    "unlimitedStorage": {
        "description": "Provides an unlimited quota for storing HTML5 client-side data.",
        "risk": "Low",
    },
    "webNavigation": {
        "description": "Grants access to the chrome.webNavigation API to receive notifications about the status of navigation requests in-flight.",
        "risk": "High",
    },
    "webRequest": {
        "description": "Grants access to the chrome.webRequest API to observe and analyze traffic and to intercept, block, or modify requests in-flight.",
        "risk": "Critical",
    },
    "webRequestBlocking": {
        "description": "Allows the extension to block or modify network requests using the webRequest API.",
        "risk": "Critical",
    },
    "<all_urls>": {
        "description": "Grants access to all URLs, allowing the extension to inject scripts and read data from any website you visit.",
        "risk": "Critical",
    },
}
