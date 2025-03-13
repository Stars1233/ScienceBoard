# Staff Manual of VM Image

## Preprocess

1. Download the image of Ubuntu 22.04 LTS and install it on VMWare Workstation.
    - assuming `cwd` of the host machine to be the root directory of this repository;
    - assuming the VM file to be under `/app/VM`;
    - assuming username and password to be `user` and `password`; don't forget to tick 'Log in automatically';

2. (GUEST) CHANGE THE DISPLAY SYSTEM FROM WAYLAND TO X11

    ```shell
    sudo sed -i 's/^#WaylandEnable=false/WaylandEnable=false/' /etc/gdm3/custom.conf
    ```

    and restart the guest machine.

3. (GUEST) Disable options of 'Blank Screen':

    ```shell
    gsettings set org.gnome.desktop.session idle-delay 0
    gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'
    ```

4. (GUEST) Change sources of `apt` and install `vm-tools` if necessary:

    ```shell
    sudo sed -i "s/cn\.//g" /etc/apt/sources.list
    sudo apt update
    sudo apt install open-vm-tools-desktop
    ```

5. (GUEST) Install `pip` and symlink for `python`:

    ```shell
    sudo apt install python-is-python3
    sudo apt install python3-pip
    ```

## Applications
### ChimeraX

1. (GUEST) Download `ucsf-chimerax_1.9ubuntu22.04_amd64.deb` at [Web Browser](https://www.cgl.ucsf.edu/chimerax/cgi-bin/secure/chimerax-get.py?file=1.9/ubuntu-22.04/ucsf-chimerax_1.9ubuntu22.04_amd64.deb) in Guest OS, then execute

    ```shell
    sudo apt install ~/Downloads/ucsf-chimerax_1.9ubuntu22.04_amd64.deb
    ```

2. (GUEST) Install toolshed of ChimeraX-states:

    ```shell
    wget https://github.com/ShiinaHiiragi/chimerax-states/archive/refs/tags/0.5.zip -P /home/user/Downloads
    unzip /home/user/Downloads/0.5.zip -d /home/user/Downloads
    chimerax --nogui --exit --cmd "devel install /home/user/Downloads/chimerax-states-0.5 exit true"
    ```

### Kalgebra
1. (GUEST) Download `aqt` and `QT 6.5.0`:

    ```shell
    pip install aqtinstall
    echo "export PATH=\$PATH:/home/user/.local/bin" >> /home/user/.bashrc
    source /home/user/.bashrc
    aqt install-qt linux desktop 6.5.0 gcc_64 -m all -O /home/user
    ```

2. (GUEST) Download `kalgebra-kai.deb` and install it:

    ```shell
    wget https://github.com/ShiinaHiiragi/kalgebra/releases/download/0.1/kalgebra-kai.deb -P /home/user/Downloads
    sudo dpkg -i /home/user/Downloads/kalgebra-kai.deb
    LD_LIBRARY_PATH=/home/user/6.5.0/gcc_64/lib /app/bin/kalgebra
    ```

## Postprocess
1. (HOST) Move server files into guest OS:

    ```shell
    vmrun -T ws -gu user -gp password runProgramInGuest /app/VM/Ubuntu.vmx /usr/bin/bash -c "mkdir /home/user/server"
    vmrun -T ws -gu user -gp password runProgramInGuest /app/VM/Ubuntu.vmx /usr/bin/bash -c "mkdir -p /home/user/.config/systemd/user"
    vmrun -T ws -gu user -gp password CopyFileFromHostToGuest /app/VM/Ubuntu.vmx vm_config/server.py /home/user/server/main.py
    vmrun -T ws -gu user -gp password CopyFileFromHostToGuest /app/VM/Ubuntu.vmx vm_config/reset.sh /home/user/server/reset.sh
    vmrun -T ws -gu user -gp password CopyFileFromHostToGuest /app/VM/Ubuntu.vmx vm_config/pyxcursor.py /home/user/server/pyxcursor.py
    vmrun -T ws -gu user -gp password CopyFileFromHostToGuest /app/VM/Ubuntu.vmx vm_config/service.conf /home/user/.config/systemd/user/osworld.service
    ```

2. (GUEST) Start daemon process:

    ```shell
    chmod +x /home/user/server/reset.sh
    pip install python-xlib lxml pyautogui Flask numpy
    sudo apt install python3-tk python3-dev ffmpeg gnome-screenshot
    gsettings set org.gnome.desktop.interface toolkit-accessibility true

    systemctl --user daemon-reload
    systemctl --user enable osworld.service
    systemctl --user restart osworld.service
    ```

3. (HOST) Attach a `__VERSION__` file under VM directory:

    ```shell
    echo "0.1" >> /app/VM/__VERSION__
    ```

4. (HOST) Compress vmware files:

    ```shell
    cd /app/VM; zip -r ../Ubuntu-x86.zip *; cd -
    ```

## References
