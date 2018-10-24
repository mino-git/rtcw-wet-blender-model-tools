
set DIR_GAME_INSTALLATION=C:\Users\nm\WETg
set MOD_NAME=legacy
set MAP_NAME=lays_of_schwarzwald_b1

set DIR_EXPORT=..\export

set MODEL_NAME=thompson.mdc

set DIR_ZIP=.\models\weapons2\thompson

copy %DIR_EXPORT%\%MODEL_NAME% %DIR_ZIP%\%MODEL_NAME%

7z.exe u -tzip z.zip animations models characters -r

copy z.zip z_sample.zip

rename z.zip z.pk3

copy z.pk3 %DIR_GAME_INSTALLATION%\%MOD_NAME%

del z.pk3

start %DIR_GAME_INSTALLATION%\etl.exe +set fs_basepath %DIR_GAME_INSTALLATION% +fs_game %MOD_NAME% +devmap %MAP_NAME% +set g_warmup 5