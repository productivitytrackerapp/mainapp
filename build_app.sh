#!/bin/bash
set -e

APP=MyTool.app

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"

cp -R src "$APP/Contents/Resources/src"

clang launcher.c -o "$APP/Contents/MacOS/launcher"

cat > "$APP/Contents/Info.plist" <<'EOF'
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>local.mytool</string>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF

codesign --force --sign pythonlocal "$APP"
codesign --verify --strict "$APP"