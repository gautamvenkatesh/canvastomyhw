from app import *



    new_hw  = check_new_hw(assignments[0], assignments[1])
    hws = date_time_title(new_hw[0], new_hw[1])

        add_hw(hws['title'][i], hws['dates'][i], hws['times'][i], hws['class'][i])
    print(datetime.now())
if __name__  == '__main__':
    main()