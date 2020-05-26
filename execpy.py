# coding=utf-8
import sys, io, subprocess
from timeout_decorator import timeout, TimeoutError

class ExecPy:
    @timeout(5)
    def execute_py(self, code):
        with open("program.py", mode="w") as f:
            f.write(code)
        try:
            res = subprocess.check_output("python3 program.py")
        except:
            res = "Can't move"
        print(res)

    async def execution(self, message):
        msg = message.content
        lines = msg.split("\n")
        if len(lines) <= 1:
            print("line nothin")
            print(lines)
            return
        
        if lines[0].startswith("py") and lines[1] == "```":
            commands = lines[0].split()
            wakeword = commands.pop(0)
            if not wakeword in ["py", "python"]:
                print("not wake word")
                return

            save = False
            repeat = 1

            for com in commands:
                if com == "save":
                    save = True
                else:
                    try:
                        v = int(com)
                        if v > 1:
                            repeat = v
                    except:
                        pass

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
                if "exit()" in code:
                    await message.channel.send("can't use exit()")
                else:
                    for _ in range(repeat):
                        with io.StringIO() as f:

                            # 標準出力を f に切り替える。
                            sys.stdout = f

                            try:
                                self.execute_py(code)
                            except TimeoutError as e:
                                print(f"Timeout")
                            except Exception as e:
                                print(str(e))
                            # f に出力されたものを文字列として取得
                            text = f.getvalue()

                            # 標準出力をデフォルトに戻して text を表示
                            sys.stdout = sys.__stdout__

                            await message.channel.send(text)
