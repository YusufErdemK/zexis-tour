# ─────────────────────────────────────────────────────────────
# ZeXis Tour — Makefile
# Kullanım:
#   make          → projeyi derle (dist/zexis-tour binary)
#   make install  → sisteme kur (sudo gerekir)
#   make clean    → derleme dosyalarını temizle
#   make run      → binary'yi çalıştır
# ─────────────────────────────────────────────────────────────

APP_NAME    = zexis-tour
MAIN        = main
DIST_DIR    = dist
BUILD_DIR   = build
INSTALL_DIR = /usr/share/zexis-tour
BINARY      = $(DIST_DIR)/$(APP_NAME)

# GTK tema ve ikon dosyaları için ekstra veri
DATA_FLAGS  = --add-data "slides.json:." \
              --add-data "ui:ui" \
              --add-data "resources:resources"

.PHONY: all build install clean run

# Varsayılan hedef
all: build

# ── Derleme ───────────────────────────────────────────────────
build:
	@echo ">>> ZeXis Tour derleniyor..."
	pyinstaller \
		--onefile \
		--name $(APP_NAME) \
		--distpath $(DIST_DIR) \
		--workpath $(BUILD_DIR) \
		--hidden-import gi \
		--hidden-import gi.repository.Gtk \
		--hidden-import gi.repository.Adw \
		--hidden-import gi.repository.GLib \
		--hidden-import gi.repository.Gio \
		--hidden-import gi.repository.GdkPixbuf \
		$(DATA_FLAGS) \
		$(MAIN)
	@echo ">>> Tamamlandı: $(BINARY)"

# ── Kurulum ───────────────────────────────────────────────────
install: build
	@if [ "$$EUID" -ne 0 ]; then \
		echo "HATA: Kurulum için sudo gerekli."; \
		echo "  sudo make install"; \
		exit 1; \
	fi
	@echo ">>> Sisteme kuruluyor..."
	mkdir -p $(INSTALL_DIR)
	cp $(BINARY) $(INSTALL_DIR)/$(APP_NAME)
	chmod +x $(INSTALL_DIR)/$(APP_NAME)
	cp zexis-tour.desktop /usr/share/applications/
	mkdir -p /etc/skel/.config/autostart
	cp zexis-tour.desktop /etc/skel/.config/autostart/zexis-tour.desktop
	@# Desktop dosyasındaki Exec= yolunu güncelle
	sed -i 's|Exec=.*|Exec=$(INSTALL_DIR)/$(APP_NAME)|' \
		/usr/share/applications/zexis-tour.desktop \
		/etc/skel/.config/autostart/zexis-tour.desktop
	@echo ">>> Kurulum tamamlandı!"

# ── Çalıştır ──────────────────────────────────────────────────
run: build
	@echo ">>> Çalıştırılıyor..."
	$(BINARY)

# ── Temizlik ──────────────────────────────────────────────────
clean:
	@echo ">>> Temizleniyor..."
	rm -rf $(DIST_DIR) $(BUILD_DIR)
	@echo ">>> Temizlik tamamlandı."