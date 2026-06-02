# QHadoop Tools

QHadoop Tools is a QGIS plugin that enables interaction with Hadoop (HDFS) using WebHDFS for managing spatial data.

---

## 🚀 Features

- Copy files **from HDFS to local**
- Upload files **from local to HDFS**
- Fix JSON / GeoJSON structure
- Input validation for connections and paths
- Support for **JSON output format**

---

## 🏗 Architecture

The plugin follows a layered architecture:

UI (views + dialogs)  
↓  
Controller  
↓  
Core services (HDFS / GeoJSON)  
↓  
Infrastructure (WebHDFS client)  

### Key Components

- **Controller** → Coordinates UI and services  
- **Core**
  - `hdfs_service` → Upload and download files
  - `geojson_service` → JSON/GeoJSON processing
- **Infrastructure**
  - `webhdfs_client` → HTTP communication with HDFS
- **UI**
  - dialogs → validation and signals
  - views → Qt Designer (`.ui` files)

---

## ⚙️ Requirements

- QGIS 3.x  
- Hadoop cluster with WebHDFS enabled  
- Network access to NameNode  

---

## ▶️ Usage

1. Open QHadoop Tools in QGIS
2. Configure connection parameters:
   - Host
   - Port (50070 or 9870 depending on configuration)
   - User
3. Click:
   - **Test Connection** → verify connectivity
   - **Copy** → execute upload or download

---

## ⚠️ Notes

- Large file uploads may require increased timeout
- Ensure WebHDFS is enabled (`dfs.webhdfs.enabled=true`)
- Output files are saved using `.json` format
- Poor network or HDFS overload may cause connection reset errors

---

## 🔧 UI Path Resolution Fix

The plugin structure was refactored to separate UI components into two layers:

- `ui/views` → Qt Designer files (.ui)
- `ui/dialogs` → dialog logic, validation and signals

### Problem

After separating the UI structure, dialogs were incorrectly resolving `.ui` file paths relative to their own directory, producing errors like:

---

## 📚 Citation

If you use this plugin in your work:

Ramírez, S. (2021). *QHadoop Tools*. QGIS Plugin.

---

## 👨‍💻 Author

Salomón Einstein  
Universidad Distrital Francisco José de Caldas  
Bogotá D.C., Colombia  

📧 seramirezf@udistrital.edu.co