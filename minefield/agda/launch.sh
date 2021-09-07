#!/bin/bash
#-------------------------------------------------------
#  Part 1: Check for and handle command-line arguments
#-------------------------------------------------------
TIME_WARP=7
JUST_MAKE="no"
HAZARD_FILE="hazards6.txt"

for ARGI; do
    if [ "${ARGI}" = "--help" -o "${ARGI}" = "-h" ] ; then
      	printf "%s [SWITCHES] [time_warp]   \n" $0
      	printf "  --just_make, -j    \n"
      	printf "  --hazards=file.txt \n"
      	printf "  --help, -h         \n"
      	exit 0;
    elif [ "${ARGI:0:10}" = "--hazards=" ] ; then
        HAZARD_FILE="${ARGI#--hazards=*}"
    elif [ "${ARGI//[^0-9]/}" = "$ARGI" -a "$TIME_WARP" = 1 ]; then
        TIME_WARP=$ARGI
    elif [ "${ARGI}" = "--just_build" -o "${ARGI}" = "-j" ] ; then
	      JUST_MAKE="yes"
    else
      	printf "Bad Argument: %s \n" $ARGI
      	exit 0
    fi
done

if [ -f $HAZARD_FILE ]; then
  echo "          Hazard File: $HAZARD_FILE"
else
  echo "$HAZARD_FILE not found. Exiting"
  exit 0
fi
#-------------------------------------------------------
#  Part 2: Create the .moos and .bhv files.
#-------------------------------------------------------

for i in {0..4}
do
  x[$i]=$(($RANDOM % 400 - 141))
  if [[ $RANDOM -gt 16383 ]]
  then
    y[$i]=$(($RANDOM % 100 - 25))
  else
    y[$i]=$(($RANDOM % 100 - 325))
  fi
done

VNAME1="remus"      # The first   vehicle community
START_POS1="${x[0]},${y[0]}"
ANGLE="0,0"

VNAME2="Altmark"      # The SHIP
START_POS2="-131,-35"
ship_angle="90,0"

VNAME3="Astron"      # The SHIP
START_POS3="-131,-55"

VNAME4="USS-Adhara"      # The SHIP
START_POS4="-131,-75"

VNAME5="USS-Alderamin"      # The SHIP
START_POS5="-131,-95"

VNAME6="SS-AmericanVictory"      # The SHIP
START_POS6="-131,-115"

VNAME7="MS-Antenor"      # The SHIP
START_POS7="-131,-135"

VNAME8="USS-Aludra"      # The SHIP
START_POS8="-131,-155"

VNAME9="USS-Albireo"      # The SHIP
START_POS9="-131,-175"

VNAME10="USS-Alkes"      # The SHIP
START_POS10="-131,-195"

VNAME11="USS-Ara"      # The SHIP
START_POS11="-131,-215"

VNAME12="fisher1"      # The SHIP
START_POS12="${x[1]},${y[1]}"

VNAME13="fisher2"      # The SHIP
START_POS13="${x[2]},${y[2]}"

VNAME14="fisher3"      # The SHIP
START_POS14="${x[3]},${y[3]}"

VNAME15="fisher4"      # The SHIP
START_POS15="${x[4]},${y[5]}"

# What is nsplug? Type "nsplug --help" or "nsplug --manual"

nsplug meta_shoreside.moos targ_shoreside.moos -f WARP=$TIME_WARP \
    VNAME="shoreside"         HAZARD_FILE=$HAZARD_FILE            \
    SHOREIP=localhost         SHORE_LISTEN=9200                   \
    MAX_TIME=$MAX_TIME        PEN_MISSED_HAZ=$PEN_MISSED_HAZ      \
    PEN_FALARM=$PEN_FALARM

nsplug meta_vehicle.moos targ_$VNAME1.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME1         START_POS=$START_POS1                \
    VPORT="9001"          SHARE_LISTEN="9301"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME1        ANGLE=$ANGLE		                       \
    VTYPE=UUV

nsplug meta_ship.moos targ_$VNAME2.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME2         START_POS=$START_POS2               \
    VPORT="9002"          SHARE_LISTEN="9302"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME2        ANGLE=$ship_angle    		                       \
    VTYPE=SHIP

nsplug meta_ship1.moos targ_$VNAME3.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME3         START_POS=$START_POS3               \
    VPORT="9003"          SHARE_LISTEN="9303"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME3        ANGLE=$ship_angle                                   \
    VTYPE=SHIP

nsplug meta_ship2.moos targ_$VNAME4.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME4         START_POS=$START_POS4               \
    VPORT="9004"          SHARE_LISTEN="9304"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME4        ANGLE=$ship_angle                                   \
    VTYPE=SHIP

nsplug meta_ship3.moos targ_$VNAME5.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME5         START_POS=$START_POS5               \
    VPORT="9005"          SHARE_LISTEN="9305"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME5        ANGLE=$ship_angle                                   \
    VTYPE=SHIP

nsplug meta_ship4.moos targ_$VNAME6.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME6         START_POS=$START_POS6               \
    VPORT="9006"          SHARE_LISTEN="9306"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME6        ANGLE=$ship_angle                                   \
    VTYPE=SHIP

nsplug meta_ship5.moos targ_$VNAME7.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME7         START_POS=$START_POS7               \
    VPORT="9007"          SHARE_LISTEN="9307"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME7        ANGLE=$ship_angle                                   \
    VTYPE=SHIP


nsplug meta_ship6.moos targ_$VNAME8.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME8         START_POS=$START_POS8               \
    VPORT="9008"          SHARE_LISTEN="9308"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME8        ANGLE=$ship_angle                                   \
    VTYPE=SHIP

nsplug meta_ship7.moos targ_$VNAME9.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME9         START_POS=$START_POS9               \
    VPORT="9009"          SHARE_LISTEN="9309"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME9        ANGLE=$ship_angle                                   \
    VTYPE=SHIP

nsplug meta_ship8.moos targ_$VNAME10.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME10         START_POS=$START_POS10               \
    VPORT="9010"          SHARE_LISTEN="9310"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME10        ANGLE=$ship_angle                                   \
    VTYPE=SHIP

nsplug meta_ship9.moos targ_$VNAME11.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME11         START_POS=$START_POS11               \
    VPORT="9011"          SHARE_LISTEN="9311"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME11        ANGLE=$ship_angle                                   \
    VTYPE=SHIP

nsplug meta_fisher1.moos targ_$VNAME12.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME12         START_POS=$START_POS12               \
    VPORT="9012"          SHARE_LISTEN="9312"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME12        ANGLE=$ANGLE                                   \
    VTYPE=GLIDER

nsplug meta_fisher2.moos targ_$VNAME13.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME13         START_POS=$START_POS13               \
    VPORT="9013"          SHARE_LISTEN="9313"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME13        ANGLE=$ANGLE                                    \
    VTYPE=KAYAK

nsplug meta_fisher3.moos targ_$VNAME14.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME14         START_POS=$START_POS14               \
    VPORT="9014"          SHARE_LISTEN="9314"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME14        ANGLE=$ANGLE                                    \
    VTYPE=KAYAK

nsplug meta_enemy.moos targ_$VNAME15.moos -f WARP=$TIME_WARP  \
    VNAME=$VNAME15         START_POS=$START_POS15               \
    VPORT="9015"          SHARE_LISTEN="9315"                  \
    SHOREIP="localhost"   SHORE_LISTEN="9200"                  \
    VNAME1=$VNAME15        ANGLE=$ANGLE                                  \
    VTYPE=GLIDER

nsplug meta_vehicle.bhv targ_$VNAME1.bhv -f VNAME=$VNAME1   \
    START_POS=$START_POS1 VNAME1=$VNAME1

nsplug meta_ship.bhv targ_$VNAME2.bhv -f VNAME=$VNAME2   \
    START_POS=$START_POS2 VNAME1=$VNAME2

nsplug meta_ship.bhv targ_$VNAME3.bhv -f VNAME=$VNAME3   \
    START_POS=$START_POS3 VNAME1=$VNAME3

nsplug meta_ship.bhv targ_$VNAME4.bhv -f VNAME=$VNAME4   \
    START_POS=$START_POS4 VNAME1=$VNAME4

nsplug meta_ship.bhv targ_$VNAME5.bhv -f VNAME=$VNAME5   \
    START_POS=$START_POS5 VNAME1=$VNAME5

nsplug meta_ship.bhv targ_$VNAME6.bhv -f VNAME=$VNAME6   \
    START_POS=$START_POS6 VNAME1=$VNAME6

nsplug meta_ship.bhv targ_$VNAME7.bhv -f VNAME=$VNAME7   \
    START_POS=$START_POS7 VNAME1=$VNAME7

nsplug meta_ship.bhv targ_$VNAME8.bhv -f VNAME=$VNAME8   \
    START_POS=$START_POS8 VNAME1=$VNAME8

nsplug meta_ship.bhv targ_$VNAME9.bhv -f VNAME=$VNAME9   \
    START_POS=$START_POS9 VNAME1=$VNAME9

nsplug meta_ship.bhv targ_$VNAME10.bhv -f VNAME=$VNAME10   \
    START_POS=$START_POS10 VNAME1=$VNAME10

nsplug meta_ship.bhv targ_$VNAME11.bhv -f VNAME=$VNAME11   \
    START_POS=$START_POS11 VNAME1=$VNAME11

nsplug meta_fisher4.bhv targ_$VNAME12.bhv -f VNAME=$VNAME12   \
    START_POS=$START_POS12 VNAME1=$VNAME12

nsplug meta_fisher4.bhv targ_$VNAME13.bhv -f VNAME=$VNAME13   \
    START_POS=$START_POS13 VNAME1=$VNAME13

nsplug meta_fisher4.bhv targ_$VNAME14.bhv -f VNAME=$VNAME14   \
    START_POS=$START_POS14 VNAME1=$VNAME14

nsplug meta_fisher4.bhv targ_$VNAME15.bhv -f VNAME=$VNAME15   \
    START_POS=$START_POS15 VNAME1=$VNAME15

if [ ${JUST_MAKE} = "yes" ] ; then
    exit 0
fi

#-------------------------------------------------------
#  Part 3: Launch the processes
#-------------------------------------------------------
printf "Launching $VNAME1 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME1.moos >& /dev/null &

printf "Launching $VNAME2 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME2.moos >& /dev/null &

printf "Launching $VNAME3 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME3.moos >& /dev/null &

printf "Launching $VNAME4 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME4.moos >& /dev/null &

printf "Launching $VNAME5 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME5.moos >& /dev/null &

printf "Launching $VNAME6 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME6.moos >& /dev/null &

printf "Launching $VNAME7 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME7.moos >& /dev/null &

printf "Launching $VNAME8 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME8.moos >& /dev/null &

printf "Launching $VNAME9 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME9.moos >& /dev/null &

printf "Launching $VNAME10 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME10.moos >& /dev/null &

printf "Launching $VNAME11 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME11.moos >& /dev/null &

printf "Launching $VNAME12 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME12.moos >& /dev/null &

printf "Launching $VNAME13 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME13.moos >& /dev/null &

printf "Launching $VNAME14 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME14.moos >& /dev/null &

printf "Launching $VNAME15 MOOS Community (WARP=%s) \n" $TIME_WARP
pAntler targ_$VNAME15.moos >& /dev/null &

printf "Launching $SNAME MOOS Community (WARP=%s) \n"  $TIME_WARP
pAntler targ_shoreside.moos >& /dev/null &
printf "Done \n"


uMAC targ_shoreside.moos

printf "Killing all processes ... \n"
kill %1 %2 %3 %4 %5 %6 %7 %8 %9 %10 %11 %12 %13 %14 %15 %16
mykill
printf "Done killing processes.   \n"
