import docx
import sqlite3
import os
from datetime import date

UP_OR_DOWN = {}

days = {"ПОНЕДЕЛЬНИК": 'monday', "ВТОРНИК": 'tuesday', "СРЕДА": 'wednesday',
        "ЧЕТВЕРГ": 'thursday', "ПЯТНИЦА": 'friday', "СУББОТА": 'saturday'}


def schedule_refresh():
    global days
    con = sqlite3.connect("DataBase.db")
    cur = con.cursor()
    tables = cur.execute('SELECT name from sqlite_master where type= "table"').fetchall()
    for elem in tables:
        if str(elem) != "('users',)":
            cur.execute(f"""DROP TABLE {str(elem)[2:-3]};""")
            con.commit()
    for name in os.listdir("schedules"):
        cur.execute(f"""CREATE TABLE {name[:-5].replace(" ", "_").replace("-", "_")}(
                    group_id STRING,
                    monday TEXT,
                    tuesday TEXT,
                    wednesday TEXT,
                    thursday TEXT,
                    friday TEXT,
                    saturday TEXT);""")
        con.commit()
        doc = docx.Document("schedules/" + name)
        tables = doc.tables
        all = {}
        for table in tables:
            if len(table.column_cells(0)) == 1 or len(table.row_cells(0)) == 2:
                pass
            else:
                if table.rows[1].cells[1].text.replace("\n", " ").replace(" ", "") == "":
                    first_start = 3
                else:
                    first_start = 2
                if table.rows[0].cells[0].text.replace(" ", "").replace("\n", "").replace("\t", "") == "" or \
                        table.rows[0].cells[0].text.replace(" ", "").replace("-", "").replace("\n", "").replace("\t",
                                                                                                                "").lower()[
                        :4] + " " \
                        + table.rows[0].cells[0].text.replace(" ", "").replace("-", "").replace("\n", "").replace("\t",
                                                                                                                  "").lower()[
                          4:] == "деньнедели":
                    for elem in table.rows[0].cells[first_start:]:
                        if elem.text.replace(" ", "").replace("\n", "") != "" and elem.text.replace(" ", "").replace(
                                "\n", "") not in days.keys():
                            all[elem.text] = {"ПОНЕДЕЛЬНИК": {}, "ВТОРНИК": {}, "СРЕДА": {},
                                              "ЧЕТВЕРГ": {}, "ПЯТНИЦА": {}, "СУББОТА": {}}
        groups = []
        for table in tables:
            dist = [0, -1]
            if len(table.column_cells(0)) == 1 or len(table.row_cells(0)) == 2:
                pass
            else:
                if table.rows[1].cells[1].text.replace("\n", " ").replace(" ", "") == "":
                    first_start = 3
                else:
                    first_start = 2
                if table.rows[0].cells[0].text.replace(" ", "").replace("\n", "").replace("\t", "") == "" or \
                        table.rows[0].cells[0].text.replace(" ", "").replace("-", "").replace("\n", "").replace("\t",
                                                                                                                "").lower()[
                        :4] + " " \
                        + table.rows[0].cells[0].text.replace(" ", "").replace("-", "").replace("\n", "").replace("\t",
                                                                                                                  "").lower()[
                          4:] == "деньнедели":
                    sp = []
                    for elem in table.rows[0].cells[first_start:]:
                        if elem.text.replace(" ", "").replace("\n", "").replace("\t", "") != "" and \
                                elem.text.replace(" ", "").replace("\n", "").upper() not in list(days.keys()):
                            sp.append(elem.text)
                    groups = sp
                    dist[0] = 1

                if len(table.rows[-1].cells) != 0:
                    for elem in table.rows[dist[0]:]:
                        if elem.cells[0].text.replace(" ", "").replace("\n", "").replace("\t", "") == "" or \
                                table.rows[0].cells[0].text.replace(" ", "").replace("-", "").lower()[:4] + " " \
                                + table.rows[0].cells[0].text.replace(" ", "").replace("-", "").lower()[
                                  4:] == "деньнедели" or \
                                elem.cells[0].text.replace(" ", "").replace("\n", "").replace("\t",
                                                                                              "").upper() in days.keys():
                            if elem.cells[0].text.replace(" ", "").replace("\n", "").replace("\t", "") == "" or \
                                    table.rows[0].cells[0].text.replace(" ", "").replace("-", "").lower()[:4] + " " \
                                    + table.rows[0].cells[0].text.replace(" ", "").replace("-", "").lower()[
                                      4:] == "деньнедели":
                                sp = []
                                for el in elem.cells[first_start:]:
                                    if el.text.replace(" ", "").replace("\n", "").replace("\t", "") != "" and \
                                            el.text.replace(" ", "").replace("\n", "").upper() not in list(days.keys()):
                                        sp.append(el.text)
                                groups = sp
                            else:
                                for i in range(len(groups)):
                                    sp = []
                                    for l in range(len(elem.cells)):
                                        el = elem.cells[l].text.replace("\n", "").replace("\t", "").strip()
                                        if el != "":
                                            if el in days and el not in sp:
                                                sp.append(el)
                                            elif el not in days:
                                                sp.append(el)
                                        elif el == "" and l != 1:
                                            sp.append(el)
                                    if sp[1] == "":
                                        while sp[1] == "":
                                            sp.remove(sp[1])
                                    group = groups[i]
                                    day = sp[0].replace("\n", "").replace(" ", "").strip()
                                    time = sp[1]
                                    lesson = sp[i + 2]
                                    if day in list(days.keys()):
                                        if lesson.replace("\n", "").replace(" ", "").strip() == "":
                                            lesson = "🎉 Отдыхаем!"
                                        if time not in all[group][day].keys():
                                            all[group][day][time] = "{{ UP_OR_DOWN }}" + "\n📚" + lesson + "\n"
                                        else:
                                            all[group][day][time] += "{{ UP_OR_DOWN }}" + f"\n📚{lesson}"

        for group in all.keys():
            for day in all[group].keys():
                dy = f":[[: START :]]:🗓 <b><<<{day}>>></b>"
                dy += "\n--------------\n"
                for time in all[group][day].keys():
                    dy += "⏳ <u>" + time.replace('\n', ' ').split(' ')[0][:11] + "</u>\n"
                    dy += "<u>Перерыв: " + time.replace('\n', ' ').split(" ")[-1] + "</u>\n:[[: START :]]:"
                    if all[group][day][time].replace('\n', ' ').replace(" ", "") == "":
                        dy += "🎉 Отдыхаем!"
                    else:
                        dy += all[group][day][time]
                    dy += ":[[: END :]]:\n________________\n\n:[[: END :]]:"
                all[group][day] = dy

        cur.execute(f"""DELETE FROM {name[:-5].replace(" ", "_").replace("-", "_")}""")
        con.commit()
        for group in all.keys():
            cur.execute(f"""INSERT INTO {name[:-5].replace(" ", "_").replace("-", "_")}
                VALUES('{group}', '{all[group]['ПОНЕДЕЛЬНИК']}', '{all[group]['ВТОРНИК']}', '{all[group]['СРЕДА']}',
                '{all[group]['ЧЕТВЕРГ']}', '{all[group]['ПЯТНИЦА']}', '{all[group]['СУББОТА']}');""")
            con.commit()


def give_faculties():
    con = sqlite3.connect("DataBase.db")
    cur = con.cursor()
    groups = cur.execute("""SELECT name from sqlite_master where type= 'table'""").fetchall()
    sp = []
    for elem in groups:
        if str(elem) != "('users',)":
            sp.append(elem[0])
    return sp


def give_groups(schedule):
    con = sqlite3.connect("DataBase.db")
    cur = con.cursor()
    groups = cur.execute(f"""SELECT group_id FROM {schedule}""").fetchall()
    sp = []
    for elem in groups:
        sp.append(elem[0])
    return sp


def join_to_group(user_id, group, faculty):
    con = sqlite3.connect("DataBase.db")
    cur = con.cursor()
    users = cur.execute("""SELECT user_id FROM users""").fetchall()
    if len(users) == 0:
        cur.execute(f"""INSERT INTO users
        VALUES('{user_id}', '{group}', '{faculty}')""")
        con.commit()
        return f"Теперь Вы учитесь в группе: <b><u>{group}</u></b>"
    for elem in users:
        if user_id == elem[0]:
            cur.execute(f"""UPDATE users
                                SET user_group = '{group}', user_faculty = '{faculty}'
                                WHERE user_id = '{user_id}'""")
            con.commit()
            return f"Теперь Вы учитесь в группе: <b><u>{group}</u></b>"
        else:
            cur.execute(f"""INSERT INTO users
            VALUES('{user_id}', '{group}', '{faculty}')""")
            con.commit()
            return f"Теперь Вы учитесь в группе: <b><u>{group}</u></b>"


def give_week(user_id):
    global days
    con = sqlite3.connect("DataBase.db")
    cur = con.cursor()
    group = cur.execute(f"""SELECT user_group, user_faculty FROM users
                            WHERE user_id = '{user_id}'""").fetchone()
    week = cur.execute(f"""SELECT monday, tuesday, wednesday, thursday, friday, saturday FROM {group[1]}
                            WHERE group_id = '{group[0]}'""").fetchall()
    week_lessons = []
    dat = str(date.today()).split("-")
    week_num = date(int(dat[0]), int(dat[1]), int(dat[2])).isocalendar().week % 2 + 1
    for elem in week[0]:
        sp = elem.split(":[[: END :]]:\n________________\n\n:[[: END :]]:")
        sch = ""
        for el in sp:
            if '🗓' in el:
                start = el[el.find(":[[: START :]]:") + 15:el.rfind(":[[: START :]]:")].replace("<<<", "").replace(
                    ">>>", "")
            else:
                start = el[:el.rfind(":[[: START :]]:")]
            if el.count("{{ UP_OR_DOWN }}") == 2:
                up = el[el.find("{{ UP_OR_DOWN }}") + 16:el.rfind("{{ UP_OR_DOWN }}")]
                down = el[el.rfind("{{ UP_OR_DOWN }}") + 16:el.rfind(":[[: END :]]:")]
                if week_num == 1:
                    lesson = up
                else:
                    lesson = down
            else:
                lesson = el[el.find("{{ UP_OR_DOWN }}") + 16:el.rfind(":[[: END :]]:")]
            sch += start + lesson + "\n________________\n\n"
        week_lessons.append(sch[:-19])
    return week_lessons


def give_day(user_id, day):
    con = sqlite3.connect("DataBase.db")
    cur = con.cursor()
    group = cur.execute(f"""SELECT user_group, user_faculty FROM users
                            WHERE user_id = '{user_id}'""").fetchone()

    day_schedule = cur.execute(f"""SELECT {day} FROM {group[1]}
                                WHERE group_id = '{group[0]}'""").fetchall()
    dat = str(date.today()).split("-")
    week_num = date(int(dat[0]), int(dat[1]), int(dat[2])).isocalendar().week % 2 + 1
    sp = day_schedule[0][0].split(":[[: END :]]:\n________________\n\n:[[: END :]]:")
    sch = ""
    for el in sp:
        if '🗓' in el:
            start = el[el.find(":[[: START :]]:") + 15:el.rfind(":[[: START :]]:")].replace("<<<", "").replace(
                ">>>", "")
        else:
            start = el[:el.rfind(":[[: START :]]:")]
        if el.count("{{ UP_OR_DOWN }}") == 2:
            up = el[el.find("{{ UP_OR_DOWN }}") + 16:el.rfind("{{ UP_OR_DOWN }}")]
            down = el[el.rfind("{{ UP_OR_DOWN }}") + 16:el.rfind(":[[: END :]]:")]
            if week_num == 1:
                lesson = up
            else:
                lesson = down
        else:
            lesson = el[el.find("{{ UP_OR_DOWN }}") + 16:el.rfind(":[[: END :]]:")]
        sch += start + lesson + "\n________________\n\n"
    return sch[:-19]


def delete():
    if os.path.isfile('parse_file.py'):
        os.remove('parse_file.py')
        print("success")
    else:
        print("File doesn't exists!")

#  schedule_refresh()
