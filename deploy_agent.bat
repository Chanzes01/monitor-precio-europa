@echo off
SET PROJECT_ID=monitor-precio-europa
SET REGION=europe-west1
SET FUNCTION_NAME=monitor-precio-europa-extract

echo Deploying Cloud Function...
call gcloud functions deploy %FUNCTION_NAME% ^
    --gen2 ^
    --runtime=python310 ^
    --region=%REGION% ^
    --source=. ^
    --entry-point=extract_dg_agri ^
    --trigger-http ^
    --allow-unauthenticated ^
    --project=%PROJECT_ID%

echo.
echo Setting up Cloud Scheduler (Daily at 08:00 AM)...
call gcloud scheduler jobs create http %FUNCTION_NAME%-trigger ^
    --location=%REGION% ^
    --schedule="0 8 * * *" ^
    --uri="https://%REGION%-%PROJECT_ID%.cloudfunctions.net/%FUNCTION_NAME%" ^
    --http-method=GET ^
    --project=%PROJECT_ID%

echo.
echo Deployment complete!
pause
