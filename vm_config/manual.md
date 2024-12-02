# Staff Manual of VM Modification

## Preprocess

1. Download Ubuntu-x86.zip, extract and load it via VMWare:

    ```shell
    wget https://huggingface.co/datasets/xlangai/ubuntu_osworld/resolve/main/Ubuntu-x86.zip -P ~/Downloads
    unzip ~/Downloads/Ubuntu-x86.zip -d ~/Downloads/Ubuntu-x86
    vmrun -T ws start ~/Downloads/Ubuntu-x86/Ubuntu.vmx
    ```

2. (VMWare) Disable 'Blank Screen':

    ```shell
    gsettings set org.gnome.desktop.session idle-delay 0
    gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'
    ```

3. (VMWare) Change sources of `apt` if necessary:

    ```shell
    sudo sed -i "s/hk\.//g" /etc/apt/sources.list
    sudo apt update
    ```

## Applications
### ChimeraX

1. Download ChimeraX:

    ```shell
    wget https://www.cgl.ucsf.edu/chimerax/cgi-bin/secure/chimerax-get.py?ident=OHeQer2RS7p7%2FOByqnlA%2BPxiuVBVQt361Rxx3wrmnvMqqejLdiY%3D&file=1.8%2Fflatpak%2FChimeraX-1.8.flatpak&choice=Notified -P ~/Downloads
    sudo flatpak install ~/Downloads/ChimeraX-1.8.flatpak
    ```

2. Install toolshed of ChimeraX-states:

    ```shell
    wget https://github.com/ShiinaHiiragi/chimerax-states/archive/refs/tags/0.5.zip -P ~/Downloads
    unzip ~/Downloads/0.5.zip -d ~/Downloads
    flatpak run edu.ucsf.rbvi.ChimeraX --nogui --exit --cmd "devel install ~/Downloads/chimerax-states-0.5 exit true"
    ```

3. (Optional) Load some of .cif files in advance to avoid bad connection.

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

## Postprocess

1. Substitute the original server file:

    ```shell
    vmrun -T ws CopyFileFromHostToGuest ~/Downloads/Ubuntu-x86/Ubuntu.vmx vm_config/config.ini /etc/systemd/system/osworld.service
    vmrun -T ws CopyFileFromHostToGuest ~/Downloads/Ubuntu-x86/Ubuntu.vmx vm_config/server.py /home/user/server/main.py
    sudo systemctl daemon-reload
    sudo systemctl restart osworld.service
    ```

2. Attach a `__VERSION__` file under :

    ```shell
    echo "0.1" >> __VERSION__
    ```

3. Compress vmware files:

    ```shell
    cd ~/Downloads/Ubuntu-x86; zip -r ../Ubuntu-x86.zip *; cd -
    ```

## References
