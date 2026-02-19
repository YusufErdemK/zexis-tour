#!/bin/bash

ACTION="$1"

# dil seçimi
echo "Language / Dil:"
echo "  1) Türkçe"
echo "  2) English"
read -p "Seçim / Choice [1/2]: " LANG_CHOICE

if [ "$LANG_CHOICE" = "1" ]; then
    MSG_ROOT_OK="Root yetkisi doğrulandı."
    MSG_INSTALL="ZeXis Tour kuruluyor..."
    MSG_REMOVE="ZeXis Tour kaldırılıyor..."
    MSG_MKDIR="Klasör oluşturuluyor..."
    MSG_COPY="Dosyalar kopyalanıyor..."
    MSG_DELETE="Dosyalar siliniyor..."
    MSG_DONE_INSTALL="Kurulum tamamlandı!"
    MSG_DONE_REMOVE="Kaldırma tamamlandı!"
    MSG_ERR_ROOT="Bu script sudo gerektirir."
else
    MSG_ROOT_OK="Root verified."
    MSG_INSTALL="Installing ZeXis Tour..."
    MSG_REMOVE="Removing ZeXis Tour..."
    MSG_MKDIR="Creating directory..."
    MSG_COPY="Copying files..."
    MSG_DELETE="Deleting files..."
    MSG_DONE_INSTALL="Installation complete!"
    MSG_DONE_REMOVE="Removal complete!"
    MSG_ERR_ROOT="This script requires sudo."
fi

# root kontrol
if [ "$EUID" -ne 0 ]; then
    echo "$MSG_ERR_ROOT"
    echo "  sudo $0 install"
    echo "  sudo $0 remove"
    exit 1
fi

echo "$MSG_ROOT_OK"

INSTALL_DIR="/usr/local/share/zexis-tour"

# ───── REMOVE MODE ─────
if [ "$ACTION" = "remove" ]; then
    echo "$MSG_REMOVE"
    echo "$MSG_DELETE"

    rm -rf "$INSTALL_DIR"
    rm -f /usr/share/applications/zexis-tour.desktop
    rm -f /etc/skel/.config/autostart/zexis-tour.desktop

    echo "$MSG_DONE_REMOVE"
    exit 0
fi

# ───── INSTALL MODE (default) ─────
echo "$MSG_INSTALL"

echo "$MSG_MKDIR"
mkdir -p "$INSTALL_DIR"

echo "$MSG_COPY"
cp -r ui "$INSTALL_DIR/"
cp main "$INSTALL_DIR/main"
cp completion.py "$INSTALL_DIR/"
cp slides.json "$INSTALL_DIR/"
cp -r resources "$INSTALL_DIR/"
cp zexis-tour.desktop /usr/share/applications/
cp zexis-tour.desktop /etc/skel/.config/autostart/

chmod +x "$INSTALL_DIR/main"

echo "$MSG_DONE_INSTALL"
