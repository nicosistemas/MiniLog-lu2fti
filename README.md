# MiniLog

Simple logger developed by LU2FTI.

<img width="1043" height="809" alt="image" src="https://github.com/user-attachments/assets/0dd9bb25-dd9e-4ca0-8199-1cc7d612d5ef" />
<br>
<br>

## RUN

- localhost:5000 or 127.0.0.1:5000 or [IP]:5000
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

## API

El MiniLog cuenta con una API que está escuchando POST.
/api/qso

### Ejemplo curl

```bash
curl -X POST http://localhost:5000/api/qso \
  -H "Content-Type: application/json" \
  -d '{
    "call": "LU1XXX",
    "mode": "CW",
    "freq": 7.074,
    "mycall": "LU2FTI"
  }'
```

Feature:

- Registry ID Call, frecuency, mode
- Add, Edit and Delete QSO on realtime
- Export to Adif format (.adi)
- Posibility to change ID
- Database on simple csv file
- UTC Hour
- Save the idcall record with the Guardar button or Enter
- Focus in ID Call
- Link to QRZ.com contacts
- API to connect with [ListererUDP](https://github.com/nicosistemas/UDPListener)

  
---

