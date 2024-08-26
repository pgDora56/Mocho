# coding=utf-8
import glob
import io
import os
import shutil
import subprocess
import sys
import datetime

TEMP_FILEPATH = "./mocho_bot_temp.py"

class ExecPy:
    def execute_py(self, author, code, filename="program", case=False, args=[]):
        if code != "":
            # 新規ファイルの場合は生成
            dt_now = datetime.datetime.now()
            with open(f"programs/{filename}.py", mode="w", encoding="utf-8") as f:
                f.write(f"# Created by {author} at {dt_now.strftime('%Y-%m-%d %H:%M:%S')}\n" + code)
                os.chmod(f"programs/{filename}.py", 0o777)
        else:
            # codeがない場合，実行するコードを生成
            with open(f"programs/{filename}.py", mode="r", encoding="utf-8") as f:
                code = f.read()
        
        code = f"mocho = {args}  # Insert by MochoBot\n\n" + code
        with open(TEMP_FILEPATH, mode="w", encoding="utf-8") as f:
            f.write(code)
            os.chmod(TEMP_FILEPATH, 0o777)

        if case:
            for c in glob.glob("case/*"):
                print(f"[{c}]")
                try:
                    testdata = subprocess.Popen(["cat", c], stdout=subprocess.PIPE)
                    python = subprocess.Popen(["timeout", "5", "python3", TEMP_FILEPATH], stdin=testdata.stdout, stdout=subprocess.PIPE)
                    print(python.stdout.peek().decode("utf-8"))
                except Exception as ex:
                    print("Execution error:", ex)
        else:
            try:
                res = subprocess.check_output(["timeout", "5", "python3", TEMP_FILEPATH])
                print(res.decode("utf-8"))
            except Exception as ex:
                print("Execution error:", ex)
        
        os.remove(TEMP_FILEPATH)

    async def execution(self, message):
        msg = message.content
        lines = msg.split("\n")
        if len(lines) <= 1:
            lines.append("")
        
        if lines[0].startswith("py") and lines[1] in ["```", "```py", "```python"]:
            commands = lines[0].split()
            wakeword = commands.pop(0)
            if not wakeword in ["py", "python"]:
                print("not wake word")
                return False

            case = False
            repeat = 1

            filename = "program"
            # for com in commands:
            while len(commands) != 0:
                com = commands.pop(0)
                try:
                    v = int(com)
                    if v > 1:
                        repeat = v
                except:
                    if com == "case":
                        case = True
                    else:
                        if com != "_":
                            filename = com
                        break

            arguments = commands # 残りは引数とする

            # ソースコード処理
            scanner = "\n".join(lines[2:])
            mark_cnt = 0
            code = ""
            is_close = False
            for c in scanner:
                code += c
                if c == "`":
                    mark_cnt += 1
                    if mark_cnt == 3:
                        code = code[:-3]
                        is_close = True
                        break
                else:
                    mark_cnt = 0
            if is_close:
                for _ in range(repeat):
                    with io.StringIO() as f:
                        # 標準出力を f に切り替える。
                        sys.stdout = f

                        try:
                            self.execute_py(message.author.name, code, filename, case, arguments)
                        except TimeoutError as e:
                            print(f"Timeout")
                        except Exception as e:
                            if "mocho_bot_temp.py" in str(e):
                              print(str(e).replace("'./mocho_bot_temp.py'", f"'{commands[1]}'"))
                            else:
                              print(str(e))
                        # f に出力されたものを文字列として取得
                        text = f.getvalue()

                        # 標準出力をデフォルトに戻して text を表示
                        sys.stdout = sys.__stdout__
                        await message.channel.send(text)
            return True

        elif lines[0].startswith("py"):
            commands = lines[0].split()
            print(commands)
            if commands[0] in ["py", "python"] and len(commands) > 1:
                if commands[1] == "watch" and len(commands) > 2:
                    try:
                        with open(f"programs/{commands[2]}.py") as f:
                            text = f"```py\n{f.read()}\n```"
                        await message.channel.send(text)
                        return True
                    except Exception as e:
                        await message.channel.send(str(e))
                        return False
                elif commands[1] == "gh" and len(commands) == 2:
                    try:
                        result = subprocess.check_output(["sh", "programs/gitpush.sh"])
                        await message.channel.send(result.decode("utf-8") + "\nhttps://github.com/pgDora56/ProgramsFromMocho")
                        return True
                    except Exception as e:
                        await message.channel.send(str(e))
                        return False
                elif os.path.exists(f"programs/{commands[1]}.py"):
                    with io.StringIO() as f:

                        # 標準出力を f に切り替える。
                        sys.stdout = f

                        try:
                            self.execute_py(message.author.name, "", commands[1], False, commands[2:])
                        except TimeoutError as e:
                            print(f"Timeout")
                        except Exception as e:
                            print(str(e).replace("'./mocho_bot_temp.py'", f"'{commands[1]}'"))
                        # f に出力されたものを文字列として取得
                        text = f.getvalue()

                        # 標準出力をデフォルトに戻して text を表示
                        sys.stdout = sys.__stdout__

                        await message.channel.send(text)
                    return True
        elif lines[0].startswith("case"):
            shutil.rmtree("case")
            os.mkdir("case")
            lines.append("")
            no = 0
            msg = ""
            for line in lines[1:]:
                if line.strip() == "":
                    if msg == "": continue
                    with open(f"case/{no}", mode="w") as f:
                        f.write(msg)
                    no += 1
                    msg = ""
                else:
                    msg += line
            return True
        return False
