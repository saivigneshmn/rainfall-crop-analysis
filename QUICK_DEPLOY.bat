@echo off
REM Quick deployment script for Windows (ngrok tunnel)

echo Starting Streamlit app...
start /B streamlit run streamlit_app.py

timeout /t 5 /nobreak

echo Starting ngrok tunnel...
start cmd /k ngrok http 8501

echo.
echo Deployment started!
echo Check the ngrok window for your public URL
echo Press any key to exit (but keep terminal open)
pause

