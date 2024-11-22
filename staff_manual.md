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

    ```
    ...
    ```

### Kalgebra

## Postprocess

1. Take a snapshot with name of `sci_bench`:

    ```shell
    vmrun -T ws /path/to/vmx snapshot sci_bench
    ```

2. Attach a `__VERSION__` file under :

    ```shell
    echo "1.0" >> __VERSION__
    ```

3. Compress vmware files:

    ```shell
    cd ~/Downloads/Ubuntu-x86; zip -r ../Ubuntu-x86.zip *; cd -
    ```
