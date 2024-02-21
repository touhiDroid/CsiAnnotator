# Print iterations progress
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()


def list_to_string(li):
    if not li or li is None or len(li) < 1:
        return ''
    s = li[0]
    for i in range(1, len(li)):
        s += '_' + li[i]
    return s


def get_proper_ann_time(ts_str):
    try:
        ts_ms = int(float(ts_str))
    except ValueError:
        return -1
    return ts_ms * 1000 if ts_ms < 99999999999 else ts_ms


def big_action_button_style():
    return """
                QPushButton {
                    background-color: #97C9FF;
                    border: 1px solid rgb(0, 0, 0, 0.1);
                    color: black;
                    padding: 10px 24px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 16px;
                    margin: 4px 2px;
                    transition-duration: 0.4s;
                    cursor: pointer;
                    border-radius: 8px;
                }

                QPushButton:hover {
                    background-color: #92C2FC;
                    border: 1px solid rgba(0, 0, 0, 0.2);
                }

                QPushButton:pressed {
                    background-color: #8DB9ED;
                    border: 1px solid rgba(0, 0, 0, 0.1);
                }
            """


def icon_only_button_style():
    return """
        QPushButton {
            background-color: #F7F7F7;
            border: 1px solid black;
            color: black;
            padding: 0px;
            margin: 0px;
            font-size: 0px;
            width: 32px;  /* Adjust width as needed */
            height: 32px; /* Adjust height as needed */
            border-radius: 16px; /* Make it a circle */
        }
        
        QPushButton:hover {
            background-color: rgba(0, 0, 0, 0.1); /* Light gray background on hover */
            border: 1px solid rgba(0, 0, 0, 0.2);
        }
        
        QPushButton:pressed {
            background-color: rgba(0, 0, 0, 0.2); /* Darker gray background when pressed */
            border: 1px solid rgba(0, 0, 0, 0.0);
        }
    """
