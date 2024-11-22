# Staff Manual of VM Modification

## Preprocess

1. Download Ubuntu-x86.zip, extract and load it via VMWare

    ```shell
    wget https://huggingface.co/datasets/xlangai/ubuntu_osworld/resolve/main/Ubuntu-x86.zip -P ~/Downloads
    ```

2. Disable 'Blank Screen'

    ```shell
    gsettings set org.gnome.desktop.session idle-delay 0
    gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'
    ```

3. Change sources of `apt` if necessary

    ```shell
    sudo sed -i "s/hk\.//g" /etc/apt/sources.list
    sudo apt update
    ```

## Applications
### ChimeraX

```python
requests.post("http://localhost:5000/setup/launch", headers={"Content-Type": "application/json"}, json={"command": ["flatpak", "run", "edu.ucsf.rbvi.ChimeraX", "--cmd", "remotecontrol rest start json true port 8080"], "shell": False}).__dict__
```

### Kalgebra
