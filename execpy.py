# coding=utf-8
import glob
import io
import os
import shutil
import subprocess
import sys

class ExecPy:
    def execute_py(self, code, filename="program", case=False):
        if code != "":
            with open(f"programs/{filename}.py", mode="w", encoding="utf-8") as f:
                f.write(code)
        if case:
            for c in glob.glob("case/*"):
                print(f"[{c}]")
                try:
                    testdata = subprocess.Popen(["cat", c], stdout=subprocess.PIPE)
                    python = subprocess.Popen(["timeout", "5", "python3", f"programs/{filename}.py"], stdin=testdata.stdout, stdout=subprocess.PIPE)
                    print(python.stdout.peek().decode("utf-8"))
                except Exception as ex:
                    print("Execution error:", ex)

        else:
            try:
                res = subprocess.check_output(["timeout", "5", "python3", f"programs/{filename}.py"])
                print(res.decode("utf-8"))
            except Exception as ex:
                print("Execution error:", ex)

    async def execution(self, message):
        msg = message.content
        lines = msg.split("\n")
        if len(lines) <= 1:
            lines.append("")
        
        if lines[0].startswith("py") and lines[1] == "```":
            commands = lines[0].split()
            wakeword = commands.pop(0)
            if not wakeword in ["py", "python"]:
                print("not wake word")
                return False

            case = False
            repeat = 1

            filename = "program"
            for com in commands:
                try:
                    v = int(com)
                    if v > 1:
                        repeat = v
                except:
                    if com == "case":
                        case = True
                    else:
                        filename = com

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
                            self.execute_py(code, filename, case)
                        except TimeoutError as e:
                            print(f"Timeout")
                        except Exception as e:
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
                if os.path.exists(f"programs/{commands[1]}.py"):
                    with io.StringIO() as f:

                        # 標準出力を f に切り替える。
                        sys.stdout = f

                        try:
                            self.execute_py("", commands[1])
                        except TimeoutError as e:
                            print(f"Timeout")
                        except Exception as e:
                            print(str(e))
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
