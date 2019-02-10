
set DIR_GAME_INSTALLATION=C:\Users\nm\WETg
set MOD_NAME=legacy
set MAP_NAME=lays_of_schwarzwald_b1

set DIR_EXPORT=..\testmodels\out

set MODEL_NAME_MDM=body.mdm
set MODEL_NAME_MDX=body.mdx

set DIR_ZIP_MDM=.\models\players\temperate\allied\engineer
set DIR_ZIP_MDX=.\animations\human\base

copy %DIR_EXPORT%\%MODEL_NAME_MDM% %DIR_ZIP_MDM%\%MODEL_NAME_MDM%

copy %DIR_EXPORT%\%MODEL_NAME_MDX% %DIR_ZIP_MDX%\%MODEL_NAME_MDX%

7z.exe u -tzip z.zip animations models characters -r

copy z.zip z_sample.zip

rename z.zip z.pk3

copy z.pk3 %DIR_GAME_INSTALLATION%\%MOD_NAME%

del z.pk3

start %DIR_GAME_INSTALLATION%\etl.exe +set fs_basepath %DIR_GAME_INSTALLATION% +fs_game %MOD_NAME% +devmap %MAP_NAME% +set g_warmup 5