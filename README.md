# Cyoa_Editor
This CYOA Story Maker &amp; Visualizer is a dual-application toolkit designed to create and map interactive branching narratives. It integrates a CustomTkinter desktop editor for deep content creation with a Streamlit web interface for real-time, graphical story mapping.


---

## 🚀 Installation & Setup

Follow these steps in order to get the environment ready.

### 1. Install Graphviz (System Requirement)

The visualizer requires the Graphviz engine to be installed on your operating system and added to your system's **PATH**.

* **Windows**:
1. Download the installer from the [Graphviz Download Page](https://graphviz.org/download/).
2. Run the `.exe` installer.
3. **Important**: During installation, select **"Add Graphviz to the system PATH for all users"** or **"Add Graphviz to the system PATH for current user"**.


* **macOS**:
```bash
brew install graphviz

```


* **Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install graphviz

```



### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name

```

### 3. Install Python Dependencies

Ensure you have Python 3.9+ installed, then run:

```bash
pip install -r requirements.txt

```

---

## 🎮 How to Use

The application is designed to be launched via the Streamlit web interface, which then manages the desktop editor process.

### 1. Start the Visualizer

Run the following command in your terminal:

```bash
streamlit run cytor.py

```

### 2. Launch the Editor

* Once the Streamlit page opens in your browser, click the **"🚀 Start Editor"** button in the control panel.
* The **CustomTkinter** editor will open in a new window.

### 3. Real-time Interaction

* **Sync**: As you save or update nodes in the Desktop Editor, the Web Visualizer will automatically refresh the graph.
* **Remote Edit**: You can select a Node ID from the dropdown in the Web Interface and click **"✏️ Edit Selected"**. This sends a command to the Desktop Editor to automatically open that specific node for editing.

---

## 🛠️ Features

* **Dynamic Graphing**: Automatically color-codes nodes (Endings: Coral, Linear: Yellow, Branching: Blue).
* **Bi-Directional Communication**: Uses `.pkl` files as a messaging bridge between the two processes.
* **Emoji Schema**: Integrated support for custom emoji-based choices.
* **Background Tasks**: Uses `asyncio` in the desktop app to poll for web commands without freezing the UI.

---

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

