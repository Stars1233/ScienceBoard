# Staff Manual of VM Image

## Preprocess

1. Download the image of Ubuntu 22.04 LTS and install it on VMWare Workstation.
    - assuming the VM file to be under `/tmp/VM`;
    - assuming username and password to be `user` and `password`;
    - assuming `cwd` to be root directory of this repository;

2. (GUEST) Disable options of 'Blank Screen':

    ```shell
    gsettings set org.gnome.desktop.session idle-delay 0
    gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'
    ```

3. (GUEST) Change sources of `apt` and install `vm-tools` if necessary:

    ```shell
    sudo sed -i "s/cn\.//g" /etc/apt/sources.list
    sudo apt update
    sudo apt install open-vm-tools-desktop
    ```

4. (GUEST) Install `pip` and symlink for `python`:

    ```shell
    sudo apt install python-is-python3
    sudo apt install python3-pip
    ```

## Applications
### ChimeraX

1. (GUEST) Download `ChimeraX-1.8.flatpak` at [Web Browser](https://www.cgl.ucsf.edu/chimerax/cgi-bin/secure/chimerax-get.py?file=1.8%2Fflatpak%2FChimeraX-1.8.flatpak) in Guest OS, then execute

    ```shell
    sudo apt install flatpak
    flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    sudo flatpak install /home/user/Downloads/ChimeraX-1.8.flatpak
    ```

2. (GUEST) Install toolshed of ChimeraX-states:

    ```shell
    wget https://github.com/ShiinaHiiragi/chimerax-states/archive/refs/tags/0.5.zip -P /home/user/Downloads
    unzip /home/user/Downloads/0.5.zip -d /home/user/Downloads
    flatpak run edu.ucsf.rbvi.ChimeraX --nogui --exit --cmd "devel install /home/user/Downloads/chimerax-states-0.5 exit true"
    ```

3. (GUEST | OPTIONAL) Load some of .cif files in advance to avoid bad connection.

    ```shell
    wget https://files.rcsb.org/download/1dns.cif -P /home/user/Downloads/ChimeraX/PDB
    wget https://files.rcsb.org/download/2olx.cif -P /home/user/Downloads/ChimeraX/PDB
    wget https://files.rcsb.org/download/3bna.cif -P /home/user/Downloads/ChimeraX/PDB
    wget https://files.rcsb.org/download/3ppd.cif -P /home/user/Downloads/ChimeraX/PDB
    wget https://files.rcsb.org/download/4r0u.cif -P /home/user/Downloads/ChimeraX/PDB
    wget https://files.rcsb.org/download/4tut.cif -P /home/user/Downloads/ChimeraX/PDB
    wget https://files.rcsb.org/download/102l.cif -P /home/user/Downloads/ChimeraX/PDB
    wget https://files.rcsb.org/download/251d.cif -P /home/user/Downloads/ChimeraX/PDB
    wget https://files.rcsb.org/download/2olx.cif -P /home/user/Downloads/ChimeraX/PDB
    flatpak run edu.ucsf.rbvi.ChimeraX --nogui --exit --cmd "alphafold match A8Z1J3"
    flatpak run edu.ucsf.rbvi.ChimeraX --nogui --exit --cmd "clear"
    ```

    or use `pack.deb` mentioned after.

### Kalgebra
1. (GUEST) Download `aqt` and `QT 6.5.0`:

    ```shell
    pip install aqtinstall
    sudo aqt install-qt linux desktop 6.5.0 gcc_64 -m all -O /home/user
    ```

2. (HOST) Compile KAlgebra

### Alternative for OPTIONAL
1. (HOST) Pack the cache and move the file into guest OS:

    ```shell
    chmod 755 -R vm_config/pack
    cd vm_config/; dpkg-deb --build pack; cd -
    vmrun -T ws -gu user -gp password CopyFileFromHostToGuest /tmp/VM/Ubuntu.vmx vm_config/pack.deb /home/user/Downloads/pack.deb
    ```

2. (GUEST) Unpack the cache and change permissions of directories:

    ```shell
    sudo dpkg -i /home/user/Downloads/pack.deb
    sudo chmod 777 -R /home/user/Downloads/ChimeraX/
    rm /home/user/Downloads/pack.deb
    ```

## Postprocess
1. (HOST) Move server files into guest OS:

    ```shell
    vmrun -T ws -gu user -gp password runProgramInGuest /tmp/VM/Ubuntu.vmx /usr/bin/bash -c "mkdir /home/user/server"
    vmrun -T ws -gu user -gp password CopyFileFromHostToGuest /tmp/VM/Ubuntu.vmx vm_config/config.ini /home/user/server/osworld.service
    vmrun -T ws -gu user -gp password CopyFileFromHostToGuest /tmp/VM/Ubuntu.vmx vm_config/server.py /home/user/server/main.py
    vmrun -T ws -gu user -gp password CopyFileFromHostToGuest /tmp/VM/Ubuntu.vmx vm_config/pyxcursor.py /home/user/server/pyxcursor.py
    ```

    (GUEST) start daemon process:

    ```shell
    sudo mv /home/user/server/osworld.service /etc/systemd/system
    pip install python-xlib lxml pyautogui Flask numpy
    sudo apt install python3-tk python3-dev
    gsettings set org.gnome.desktop.interface toolkit-accessibility true

    sudo systemctl daemon-reload
    sudo systemctl enable osworld.service
    sudo systemctl restart osworld.service
    ```

2. (HOST) Attach a `__VERSION__` file under VM directory:

    ```shell
    echo "0.1" >> /tmp/VM/__VERSION__
    ```

3. (HOST) Compress vmware files:

    ```shell
    cd /tmp/VM; zip -r ../Ubuntu-x86.zip *; cd -
    ```

## References
