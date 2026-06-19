#!/bin/bash

cd /tmp && wget https://raw.githubusercontent.com/GlitchLinux/git-toolkit-gui/refs/heads/main/glitch-toolkit-gui.py
sudo mv glitch-toolkit-gui.py /usr/local/bin/glitch-toolkit-gui.py

sudo cp -f /usr/local/bin/apps /usr/local/bin/apps-cli

echo '#!/bin/bash' > /tmp/apps-gui
echo 'python3 /usr/local/bin/glitch-toolkit-gui.py 2>&1 &' >> /tmp/apps-gui
sudo mv /tmp/apps-gui /usr/local/bin/ && sudo cp /usr/local/bin/apps-gui /usr/local/bin/apps
sudo chmod +x /usr/local/bin/glitch-toolkit-gui.py
sudo chmod +x /usr/local/bin/apps && sudo chmod +x /usr/local/bin/apps-gui

echo '#!/bin/bash' > /usr/local/bin/apps-cli-restore
echo "sudo cp /usr/local/bin/apps-cli /usr/local/bin/apps" >> /usr/local/bin/apps-cli-restore
echo "echo '"apps" shortcut restored to cli toolkit'" >> /usr/local/bin/apps-cli-restore
sudo chmod +x /usr/local/bin/apps-cli-restore

echo '#!/bin/bash' > /usr/local/bin/apps-gui-restore
echo "sudo cp /usr/local/bin/apps-gui /usr/local/bin/apps" >> /usr/local/bin/apps-gui-restore
echo "echo '"apps" shortcut restored to gui toolkit'" >> /usr/local/bin/apps-gui-restore
sudo chmod +x /usr/local/bin/apps-gui-restore

echo "Glitch CLI-tookit changed to 'apps-cli' shortcut"

echo "Glitch GUI-toolkit can now be launched with 'apps' & 'apps-gui' commands"

echo "To Change 'apps' shortcut to execute CLI toolkit run 'apps-cli-restore'"
echo "OR change back 'apps' shortcut to execute GUI toolkit with 'apps-gui-restore'"










