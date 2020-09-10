filename='fairness_refactor/commands.txt'

command rm $filename
command python3.6 fairness_refactor/scripts.py

while read line; do
    # reading each line
    echo $line
    command $line
    wait $! 
done < $filename