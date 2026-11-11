(XDG-Desktop-Portal-WebExtensions-test-plan)=
# XDG Desktop Portal WebExtensions test plan


## Set up (only must be done once)

Executing these commands will create (and overwrite):

* `~/pingpong.py`
* `~/manifest.json`
* `~/background.js`
* `~/.mozilla/native-messaging-hosts/pingpong.json`

You may remove them after the test is completed.


### Native application

Execute

```none
>$HOME/pingpong.py cat <<-'EOF'
import sys
import json
import struct
def getMessage():
	rawLength = sys.stdin.buffer.read(4)
	if len(rawLength) == 0:
		sys.exit(0)
	messageLength = struct.unpack('@I', rawLength)[0]
	message = sys.stdin.buffer.read(messageLength).decode('utf-8')
	return json.loads(message)
def encodeMessage(messageContent):
	encodedContent = json.dumps(messageContent, separators=(',', ':')).encode('utf-8')
	encodedLength = struct.pack('@I', len(encodedContent))
	return {'length': encodedLength, 'content': encodedContent}
def sendMessage(encodedMessage):
	sys.stdout.buffer.write(encodedMessage['length'])
	sys.stdout.buffer.write(encodedMessage['content'])
	sys.stdout.buffer.flush()
while True:
	receivedMessage = getMessage()
	if receivedMessage == "ping":
		sendMessage(encodeMessage("native app sends pong"))
EOF
chmod +x $HOME/pingpong.py
```

```none
>$HOME/manifest.json cat <<\EOF
{
  "description": "Native messaging example add-on",
  "manifest_version": 2,
  "name": "Native messaging example",
  "version": "1.0",
  "browser_specific_settings": {
    "gecko": {
      "id": "pingpong@example.org",
      "strict_min_version": "50.0"
    }
  },
  "background": {
    "scripts": ["background.js"]
  },
  "permissions": ["nativeMessaging"]
}
EOF
```

```none
mkdir -p $HOME/.mozilla/native-messaging-hosts
> $HOME/.mozilla/native-messaging-hosts/pingpong.json cat <<END
{
  "name": "pingpong",
  "description": "Example host for native messaging",
  "path": "$HOME/pingpong.py",
  "type": "stdio",
  "allowed_extensions": [ "pingpong@example.org" ]
}
END
```

```none
> $HOME/background.js cat <<\END
let port = browser.runtime.connectNative("pingpong");
port.onMessage.addListener((response) => {
  console.log("Received: " + response);
  window.alert("Received.");
});
port.onDisconnect.addListener((port) => {
  if (port.error) {
    console.log(`Disconnected due to an error: ${port.error.message}`);
  } else {
    console.log(`Disconnected`, port);
  }
});
console.log(">>Sending: ping<<");
port.postMessage("ping");
END
```


## Portal WebExtensions test

```none
firefox about:debugging#/runtime/this-firefox
```

* "Load temporary add-on".
* Pick `~/manifest.json`.
* Confirm that the Portal dialogue appears and grant permission to the application.
* In the Firefox tool bar, click the puzzle piece button and click your extension.
* In the Firefox window, click the inspect button next to your extension.
* In the browser console that opens, click "{spellexception}`Multiprocess` view".
* Confirm that the log contains the pong response from the native application.


## Clean-up

```none
dbus-send --print-reply --dest=org.freedesktop.impl.portal.PermissionStore /org/freedesktop/impl/portal/PermissionStore org.freedesktop.impl.portal.PermissionStore.DeletePermission string:webextensions string:pingpong string:""
rm ~/pingpong.py ~/manifest.json ~/background.js ~/.mozilla/native-messaging-hosts/pingpong.json
```
