# Staff Manual of VM Modification

## Preprocess

1. Download the image of Ubuntu 22.04 LTS and install it on VMWare Workstation. Assuming the VM file to be under `/tmp/VM`.

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

## Applications
### ChimeraX

1. (GUEST) Download ChimeraX:

    ```shell
    wget https://www.cgl.ucsf.edu/chimerax/cgi-bin/secure/chimerax-get.py?ident=OHeQer2RS7p7%2FOByqnlA%2BPxiuVBVQt361Rxx3wrmnvMqqejLdiY%3D&file=1.8%2Fflatpak%2FChimeraX-1.8.flatpak&choice=Notified -P ~/Downloads
    sudo flatpak install ~/Downloads/ChimeraX-1.8.flatpak
    ```

2. (GUEST) Install toolshed of ChimeraX-states:

    ```shell
    wget https://github.com/ShiinaHiiragi/chimerax-states/archive/refs/tags/0.5.zip -P ~/Downloads
    unzip ~/Downloads/0.5.zip -d ~/Downloads
    flatpak run edu.ucsf.rbvi.ChimeraX --nogui --exit --cmd "devel install ~/Downloads/chimerax-states-0.5 exit true"
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
    ```

    and the following takes tons of time:

    ```shell
    flatpak run edu.ucsf.rbvi.ChimeraX --nogui --exit --cmd "alphafold match A8Z1J3"
    flatpak run edu.ucsf.rbvi.ChimeraX --nogui --exit --cmd "clear"
    ```

### Kalgebra
1. (GUEST) Download `aqt` and `QT 6.5.0`:

    ```shell
    pip install aqtinstall
    sudo aqt install-qt linux desktop 6.5.0 gcc_64 -m all -O /home/user
    ```

2. (HOST) Compile KAlgebra

## Postprocess

1. (HOST) Move server files into guest OS:

    ```shell
    vmrun -T ws CopyFileFromHostToGuest /tmp/VM/Ubuntu.vmx vm_config/config.ini /etc/systemd/system/osworld.service
    vmrun -T ws CopyFileFromHostToGuest /tmp/VM/Ubuntu.vmx vm_config/server.py /home/user/server/main.py
    vmrun -T ws CopyFileFromHostToGuest /tmp/VM/Ubuntu.vmx vm_config/pyxcursor.py /home/user/server/pyxcursor.py
    ```

    (GUEST) start daemon process:

    ```shell
    sudo systemctl daemon-reload
    sudo systemctl restart osworld.service
    ```

2. (HOST) Attach a `__VERSION__` file under :

    ```shell
    echo "0.1" >> __VERSION__
    ```

3. (HOST) Compress vmware files:

    ```shell
    cd /tmp/VM; zip -r ../Ubuntu-x86.zip *; cd -
    ```

## References
