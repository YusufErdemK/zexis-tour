#!/bin/bash

# root yetki kontrol falan filan
if [ "$EUID" -ne 0 ]; then
    echo "ZeXis Tur indirmek için root yetkisine ihtiyacınız var. Tekrar deneyin:"
    echo "  sudo $0"
    exit 1
fi

echo "Root yetkisi doğrulandı. ZeXis Tour kuruluyor..."

mkdir /usr/share/zexis-tour
cp -r ui /usr/share/zexis-tour/
cp main.py /usr/share/zexis-tour/
cp slides.json /usr/share/zexis-tour/
cp zexis-tour.desktop /usr/share/applications/
cp zexis-tour.desktop /etc/skel/.config/autostart/zexis-tour.desktop
cp -r resources/* /usr/share/zexis-tour/resources/

chmod +x /usr/share/zexis-tour/main.py
