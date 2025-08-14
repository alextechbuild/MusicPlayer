# MusicPlayer.py
#
# Copyright 2025 Alex-Build
#
# This Source Code Form is subject to the terms of the GPL
# License, v. 3.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.








# Libraries








import sys, random
from PyQt6.QtCore import Qt, QUrl, QTime
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QSlider, QListWidget, QListWidgetItem
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput








# Functionnalities MusicPlayer








def ms_to_time(ms):
    
    if ms <= 0:
        return "00:00"
    
    t = QTime(0, 0).addMSecs(ms)
    
    return t.toString("hh:mm:ss") if ms >= 3600000 else t.toString("mm:ss")




class MusicPlayer(QWidget):
    
    def __init__(self):
        
        super().__init__()
        self.setWindowTitle("Music Player 🎵")
        self.resize(600, 350)

        # Core
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)

        self.playlist = []         # liste des chemins de fichiers
        self.index_courant = -1
        self.is_shuffled = False
        self.is_looping = False
        self.user_dragging = False

        # Widgets
        self.label_titre = QLabel("Aucune piste")
        self.list_widget = QListWidget()
        self.slider_position = QSlider(Qt.Orientation.Horizontal)
        self.slider_position.setRange(0, 0)
        self.label_temps = QLabel("00:00 / 00:00")

        self.slider_volume = QSlider(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(100)
        self.audio.setVolume(1.0)

        self.button_previous = QPushButton("⏮️")
        self.button_play = QPushButton("▶️")
        self.button_pause = QPushButton("⏸️")
        self.button_stop = QPushButton("⏹️")
        self.button_next = QPushButton("⏭️")
        self.button_add = QPushButton("➕ Ajouter")
        self.button_shuffle = QPushButton("🔀")
        self.button_loop = QPushButton("🔁")
        self.button_mute = QPushButton("🔊")

        # Layout
        main = QVBoxLayout()
        main.addWidget(self.label_titre)
        main.addWidget(self.list_widget)
        main.addWidget(self.slider_position)
        main.addWidget(self.label_temps)

        controls = QHBoxLayout()
        controls.addWidget(self.button_previous)
        controls.addWidget(self.button_play)
        controls.addWidget(self.button_pause)
        controls.addWidget(self.button_stop)
        controls.addWidget(self.button_next)
        controls.addStretch()
        controls.addWidget(self.button_add)
        main.addLayout(controls)

        extras = QHBoxLayout()
        extras.addWidget(self.button_shuffle)
        extras.addWidget(self.button_loop)
        extras.addStretch()
        extras.addWidget(QLabel("Volume"))
        extras.addWidget(self.slider_volume)
        extras.addWidget(self.button_mute)
        main.addLayout(extras)

        self.setLayout(main)

        # Connexions
        self.button_add.clicked.connect(self.ajouter_fichiers)
        self.button_play.clicked.connect(self.jouer)
        self.button_pause.clicked.connect(self.player.pause)
        self.button_stop.clicked.connect(self.player.stop)
        self.button_previous.clicked.connect(self.precedent)
        self.button_next.clicked.connect(self.suivant)
        self.button_shuffle.clicked.connect(self.toggle_shuffle)
        self.button_loop.clicked.connect(self.toggle_loop)
        self.button_mute.clicked.connect(self.toggle_mute)

        self.list_widget.itemDoubleClicked.connect(self.jouer_selection)

        self.slider_position.sliderPressed.connect(self.on_slider_pressed)
        self.slider_position.sliderReleased.connect(self.on_slider_released)
        self.slider_position.sliderMoved.connect(self.on_slider_moved)

        self.slider_volume.valueChanged.connect(self.on_volume_changed)

        self.player.positionChanged.connect(self.on_position_changed)
        self.player.durationChanged.connect(self.on_duration_changed)
        self.player.mediaStatusChanged.connect(self.on_media_status_changed)


    # Gestion fichiers
    def ajouter_fichiers(self):
        
        fichiers, _ = QFileDialog.getOpenFileNames(
            self, "Ajouter fichiers audio", "",
            "Audio (*.mp3 *.wav *.ogg *.flac *.m4a);;Tous les fichiers (*)"
        )
        
        for f in fichiers:
            
            self.playlist.append(f)
            item = QListWidgetItem(f.split("/")[-1])
            self.list_widget.addItem(item)
            
        if self.index_courant == -1 and self.playlist:
            self.index_courant = 0
            self.charger_piste(0)

    def charger_piste(self, index):
        
        if 0 <= index < len(self.playlist):
            
            self.index_courant = index
            fichier = self.playlist[index]
            self.player.setSource(QUrl.fromLocalFile(fichier))
            self.label_titre.setText(fichier.split("/")[-1])
            self.list_widget.setCurrentRow(index)

    # Lecture
    def jouer(self):
        
        if self.index_courant == -1 and self.playlist:
            self.charger_piste(0)
            
        self.player.play()

    def jouer_selection(self, item):
        
        index = self.list_widget.currentRow()
        self.charger_piste(index)
        self.player.play()

    def precedent(self):
        
        if not self.playlist: return
        
        if self.player.position() > 3000:
            self.player.setPosition(0)
        else:
            
            if self.is_shuffled:
                self.charger_piste(random.randint(0, len(self.playlist) - 1))
            else:
                self.charger_piste((self.index_courant - 1) % len(self.playlist))
            self.player.play()

    def suivant(self):
        
        if not self.playlist: return
        
        if self.is_shuffled:
            self.charger_piste(random.randint(0, len(self.playlist) - 1))
        else:
            self.charger_piste((self.index_courant + 1) % len(self.playlist))
        self.player.play()

    # Mode
    def toggle_shuffle(self):
        
        self.is_shuffled = not self.is_shuffled
        self.button_shuffle.setStyleSheet("font-weight: bold;" if self.is_shuffled else "")

    def toggle_loop(self):
        
        self.is_looping = not self.is_looping
        self.button_loop.setStyleSheet("font-weight: bold;" if self.is_looping else "")

    # Volume
    def toggle_mute(self):
        
        muted = self.audio.isMuted()
        self.audio.setMuted(not muted)
        self.button_mute.setText("🔇" if not muted else "🔊")

    def on_volume_changed(self, value):
        
        self.audio.setVolume(value / 100.0)

    # Slider position
    def on_slider_pressed(self):
        
        self.user_dragging = True

    def on_slider_released(self):
        
        self.user_dragging = False
        self.player.setPosition(self.slider_position.value())

    def on_slider_moved(self, value):
        
        self.label_temps.setText(f"{ms_to_time(value)} / {ms_to_time(self.player.duration())}")

    # Signaux player
    def on_position_changed(self, pos):
        
        if not self.user_dragging:
            self.slider_position.setValue(pos)
            
        self.label_temps.setText(f"{ms_to_time(pos)} / {ms_to_time(self.player.duration())}")

    def on_duration_changed(self, dur):
        
        self.slider_position.setRange(0, dur)

    def on_media_status_changed(self, status):
        
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            
            if self.is_looping:
                self.player.setPosition(0)
                self.player.play()
            else:
                self.suivant()








# Main Program








if __name__ == "__main__":
    
    
    
    
    app = QApplication(sys.argv)
    fen = MusicPlayer()
    fen.show()
    sys.exit(app.exec())

