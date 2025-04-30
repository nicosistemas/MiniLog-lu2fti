# MiniLog

Simple logger developed by LU2FTI.
<br>
<br>
Run to localhost:5000 or 127.0.0.1:5000 or [IP]:5000
<br>
<br>
- Run
  
`pip install Flask`

`python3 app.py`
<br>
<br>
- Run Docker:

`docker build -t minilog . `

`docker run -d -p 5000:5000 --name minilog minilog`
<br>
<br>
- Run Windows:

(tener instalado Python)
  
`python -m venv venv`

`venv\Scripts\activate`

`pip install -r requirements.txt`  or `pip install Flask`

`python app.py`

para desactivar el entorno: deactivate

---

Feature:

- Registry ID Call, frecuency, mode
- Export to Adif format (.adi)
- Posibility to change ID
- Database on simple csv file
- UTC Hour
- Save the idcall record with the Guardar button or Enter
- Focus in ID Call
- Link to QRZ.com contacts

  
---


![image](https://github.com/user-attachments/assets/5befdb3c-f4b0-4b11-80cf-ee3a10d16167)
