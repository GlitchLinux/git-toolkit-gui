#!/bin/bash

cd /tmp && wget https://raw.githubusercontent.com/GlitchLinux/git-toolkit-gui/refs/heads/main/glitch-toolkit-gui.py
sudo mv glitch-toolkit-gui.py /usr/local/bin/glitch-toolkit-gui.py
echo '#!/bin/bash' > /tmp/apps-gui
echo 'python3 /usr/local/bin/glitch-toolkit-gui.py 2>&1 &' >> /tmp/apps-gui
sudo chmod +x /usr/local/bin/glitch-toolkit-gui.py
sudo cp /tmp/apps-gui /usr/local/bin/apps-gui
sudo chmod +x /usr/local/bin/apps-gui && sudo chown x:x /usr/local/bin/apps-gui




