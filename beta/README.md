### S.TASER CLI version

#### How to use the tool

---

1. pip install -r requirements.txt
1. python 241209_S.TASER.py -h -> show help


1. General usage
1. python 241209_S.TASER.py -s 'SmartThings directory' -f 'Samsungfind directory' -o 'output foler path (path must exist before using the tool)'

1. Applications' directory structure example and command for running the tool.
   S4-1 (scenario directory)--- com.samsung.android.oneconnect   <------ SmartThings (ST), SmartThings Find (STF)
   S4-1 ---- com.samsung.android.app.find <--------- Samsung Find (SF)

   > python 241209_S.TASER.py -s com.samsung.android.oneconnect -f com.samsung.android.app.find -o ./output

1. Then program requires sqlite DB name for storing artifacts > s4-1.db (anything is ok)

1. If the tool succussfully finish in output directory, you can find results (txt, db, html)
   
                                     


