class InterBot:
    "Communication interface for cross-script interactions"
    
    def __init__(self,ip:str="127.0.0.1",port:int=42069):
        "Will listen on `127.0.0.1:42069` (by default) for cross-script bot interactions"

        self.command_list=(
            "ret", # retrieve / query data
            "set", # set / modify data
            "dgn", # diagnostics
            "off", # power off / shutdown
            "bbt", # basementbot command interactions
            "res", # resolves a discord ID to an object
        )

        self.sock=socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
        address=(ip,port)
        try: self.sock.bind(address)
        except OSError: print("[InterBot] Ignoring socket already in use...")
        self.sock.listen()
        self.connection_handler=threading.Thread(target=self.handle_connections)

        self.connection_handler.start()


    def handle_connections(self):
        self.connection_handler_pid:int=os.getpid()
        
        while 1:
            try:
                # dear future josh: what's happening is the line below this is blocking the entire while loop. no matter what, it stops on `sock.accept()`.
                connection,addr=self.sock.accept()
                while 1:
                    data=connection.recv(4096).decode()
                    if not data: break
                    status=self.handle_command(data,connection,addr)
                    if status: self.handle_status(status)

                connection.close()

            except Exception as e:
                #print("[InterBot] Connection error: "+repr(e))
                print_exc()

        print(f"[InterBot] Connection listener closed...")
        self.sock.close()
        print("I exited")
        sys.exit()

    def handle_command(self,command:str,connection:socket.socket,address:tuple[str,int]):
        """
        Will execute a InterBot command, otherwise it will throw an error.\n
        Commands are three letters in length and some take `;`-seperated agruments.\n
        All return are in the form: `suc/err <operation> [specific data]`.\n
        The `ret` command requires `;`-seperated path to data and returns desired data.\n
        The `set` command requires `;`-seperated path to data and returns a confirmation of change.\n
        The `dgn` command will return a diagnostic report.\n
        The `off` command will shut off the bot interface.\n
        """
        execute=command[:3]
        args=self.parse_args(command[3:])

        if not execute in self.command_list:
            connection.send(f"err cmd {execute}".encode())
            return 1 # error code 1, unknown command

        else:
            try:
                if execute=="dgn": # diagnostics
                    dgn=f"upt:{BOOT_TIME};"
                    dgn+=f"cpu:{psutil.cpu_count()};"
                    dgn+=f"cpr:{psutil.cpu_percent()};"
                    dgn+=f"ram:{psutil.virtual_memory().available};"
                    dgn+=f"rpr:{psutil.virtual_memory().percent};"
                    dgn+=f"pid:{self.connection_handler_pid};"
                    connection.send(dgn.encode())
                elif execute=="ret":
                    # by accident, requests for the entirety of client.Data cannot be made, however this may prove to be useful
                    target=client.Data
                    for arg in args:
                        try: target=target[arg]
                        except KeyError:
                            connection.send(f"err {arg}".encode())
                            return 2 # error code 2, retrieve error
                    else:
                        targetPath=";".join(str(arg) for arg in args)
                        toSend=f"suc {targetPath}={target}"
                        connection.send(toSend.encode())
                        return 0
                elif execute=="set":
                    try:
                        targetPath=args
                        if "]" in command or not "=" in args[-1]:
                            connection.send(f"err arg".encode())
                            return 4 # error code 4, possible attempt to exec code
                        target=args[-1].split("=")[1]
                        args[-1]=args[-1].split("=")[0]
                        #for arg in args:
                        #    print(arg,type(arg))
                        #print(target,type(target))
                        #print(target.isdigit())
                        execCommand="client.Data"+"".join(f"[{arg}]" if arg.isdigit() else f"[\"{arg}\"]" for arg in args)
                        execCommand+="="+str(target if target.isdigit() or target in ("True","False") else f"\"{target}\"")
                        # this can possibly be exploited, but i think checking for "]" should be good enough
                        exec(execCommand)
                        # check to make sure it worked
                        checkTarget=client.Data
                        for arg in args:
                            checkTarget=checkTarget[arg]
                        #print(checkTarget, target)
                        if str(checkTarget)!=str(target).replace('"',"'"):
                            connection.send(f"err set exe".encode())
                            return 5 # error code 5, execute error
                        else:
                            connection.send(f"suc set".encode())
                    except KeyError as ke:
                        connection.send(f"err set 404 {ke.args[0]}".encode())
                        return 7 # error code 7, not found
                    except:
                        print_exc()
                        connection.send(f"err set".encode())
                        return 3 # error code 3, set error
                elif execute=="off":
                    try:
                        self.isListening=False
                        os.system(f"kill -9 {self.connection_handler_pid}")
                        ip,port=address
                        _dt=datet.now().strftime("%m/%d/%Y %H:%M:%S")
                        print(f"{_dt} [INTERBOT] Disconnected server by {ip}:{port}")
                    except:
                        connection.send(f"err off".encode())
                        return 6
                
                elif execute=="bbt":
                    connection.send(f"suc msg:This feature is still being developed.".encode())
                
                elif execute=="res":
                    # resolves ids to a variety of discord items, returns the representation of that item, client is expected to decode repr
                    if len(args)==1 and type(args[0])==int:
                        basem:discord.Guild=client.basement
                        converters=(basem.get_channel,basem.get_member,basem.get_role,client.get_emoji)
                        for converter in converters:
                            conv=converter(args[0])
                            if type(conv) in (discord.channel.TextChannel,discord.channel.VoiceChannel,discord.member.Member,discord.role.Role,discord.emoji.Emoji):
                                connection.send(f"repr={json.dumps(conv.__dict__())}".encode())
                                return 0
                                """
                                *added the following code to discord.member python file at line 235:*
                                def __dict__(self):
                                    return {
                                        'id': f'{self_user.id}',
                                        'type': 'member',
                                        'name': f'{self._user.name}',
                                        'discriminator': f'{self._user.discriminator}',
                                        'bot': f'{self._user.bot}',
                                        'nick': f'{self.nick}',
                                        'guild': f'{self.guild}'
                                    }
                                *added the following code to discord.channel python file for TextChannel and VoiceChannel respectively*
                                def __dict__(self):
                                    attrs = [
                                        ('id', self.id),
                                        ('type', 'text channel'),
                                        ('name', self.name),
                                        ('position', self.position),
                                        ('nsfw', self.nsfw),
                                        ('news', self.is_news()),
                                        ('category_id', self.category_id)
                                    ]
                                    return dict(attrs)
                                ############################################
                                def __dict__(self):
                                    attrs = [
                                        ('id', self.id),
                                        ('type', 'voice channel'),
                                        ('name', self.name),
                                        ('rtc_region', self.rtc_region),
                                        ('position', self.position),
                                        ('bitrate', self.bitrate),
                                        ('user_limit', self.user_limit),
                                        ('category_id', self.category_id)
                                    ]
                                    return dict(attrs)
                                *added the following code to discord.role python file for Role*
                                def __dict__(self):
                                    attrs = {
                                        'id': self.id,
                                        'type': 'role',
                                        'name': self.name,
                                        'color': self._colour,
                                        'mentionable': self.mentionable,
                                        'position': self.position
                                    }
                                    return attrs
                                *added the following code to discord.emoji python file for Emoji*
                                def __dict__(self):
                                    attrs={
                                        'id': self.id,
                                        'type': 'emoji',
                                        'name': self.name,
                                        'animated': self.animated,
                                        'managed': self.managed,
                                        'url': self.url.BASE+self.url._url
                                    }
                                    return attrs
                                """
                        else:
                            connection.send("err res arg msg:Is not a valid ID or type".encode())
                    else:
                        connection.send(f"err res arg msg:Only one expected".encode())
                        return 8 # error code 8, argument error

            except Exception as e:
                #connection.send(f"err {execute};{repr(e)}\n{e}".encode())
                print_exc()
                return -1 # error code -1, general failure
            
            else:
                return 0 # error code 0, success


    def parse_args(self,args:str):
        args=args.strip()
        return [int(arg) if arg.isdigit() else arg for arg in args.split(";")]


    def handle_status(self,status:int):
        if status==0:
            message="Succeeded"
        elif status==1:
            message="Unknown command"
        elif status==2:
            message="Retrieval error"
        elif status==3:
            message="Set error"
        elif status==-1:
            message="Uncaught error during runtime"
        elif status==7:
            message="Set unsuccessful, could not verify change"
        elif status==8:
            message="Argument error."
        else:
            message="Unknown error code"
        
        print("[InterBot] "+message)
