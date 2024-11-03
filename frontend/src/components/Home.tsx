import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import React, { useState, useEffect } from "react";

import { Marked } from '@ts-stack/markdown';

type Chat = {
    sender: string;
    message: string;
    img?: string | null;
    timestamp?: string; // HH:MM AM/PM
};

export const Home: React.FC = () => {
    const [query, setQuery] = useState<string>("");
    // const [info, setInfo] = useState<string>("");
    const [chats, setChats] = useState<Chat[]>([]);
    const [imageSrc, setImageSrc] = useState<string>("");

    const chatRef = React.useRef<HTMLDivElement>(null);

    const [isAtTop, setIsAtTop] = useState<boolean>(true);

    const [isResponding, setIsResponding] = useState<boolean>(false);

    const pushChat = (sender: string, message: string, img?: string | null) => {
        setChats((prev) => [...prev, { sender, message, img, timestamp: new Date().toLocaleTimeString() }]);
        setTimeout(() => {
            chatRef.current?.scrollTo({
                top: chatRef.current.scrollHeight,
                behavior: "smooth",
            })
        }, 100);
    };

    useEffect(() => {
        if (chatRef.current) {
            const check = () => {
                if (chatRef.current) {
                    setIsAtTop(chatRef.current.scrollTop === 0);
                }
            }

            chatRef.current.addEventListener("scroll", check);

            return () => {
                chatRef.current?.removeEventListener("scroll", check);
            }
        }
    }, [chatRef]);

    const handleDetect = () => {

        if (isResponding) return;

        // if query is not whitespace
        if (query.trim() === "") return;


        // setInfo(`${query}`); // something happens here
        pushChat("user", query);
        setQuery("");
        setIsResponding(true);

        fetch("https://vectorapi.hacktx24.tech/question", {
        // fetch("http://localhost:8765/question", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "accept": "application/json",
            },
            body: JSON.stringify({ "question": query }),
        })
            .then((res) => res.json())
            .then((data) => {
                pushChat("bot", data.response, data.img);
                setIsResponding(false);
            })
            .catch((err) => {
                console.error(err);
                pushChat("bot", "An error occurred while processing the request");
                setIsResponding(false);
            })

    };

    useEffect(() => {
        const ws = new WebSocket("ws://localhost:8000");

        ws.onopen = () => {
            console.log("WebSocket connection established");
        };

        ws.onmessage = (event) => {
            const image = event.data;
            setImageSrc(`data:image/jpeg;base64,${image}`);
        }

        ws.onclose = () => {
            console.log("WebSocket connection closed");
        };

        return () => {
            ws.close();
        };
    }, []);

    return (
        <div className="flex flex-col justify-start items-center h-screen max-h-screen overflow-hidden bg-gradient-to-br from-blue-500 to-purple-600">
            <h1 className="text-center text-5xl font-extrabold mb-6 text-yellow-300 mt-10">SUS DETECTOR</h1>

            <div className="w-full max-w-xl h-80 mb-2">
                {imageSrc ? <img
                    src={imageSrc}
                    alt="Live Stream"
                    className="w-full h-full object-cover rounded-lg"
                /> : <div className="w-full h-full bg-gray-800 flex justify-center items-center rounded-lg animate-pulse">
                    <p className="text-yellow-300">Connecting...</p>
                </div>}
            </div>

            {/* {info != "" && <div className="p-4 bg-gray-800 border border-yellow-500 rounded-lg mt-4">
                <p className="text-yellow-300">{info}</p>
            </div>} */}
            {chats.length > 0 && <div className="relative w-full h-full overflow-hidden max-w-xl mt-4 mb-4 animate-max-h">

                <div className={cn("flex pointer-events-none justify-center transition-all duration-300 absolute top-0 left-0 h-16 w-full bg-gradient-to-b from-black/15 to-transparent", isAtTop ? "opacity-0" : "opacity-100")} />


                <div ref={chatRef} className="gap-1 flex flex-col  w-full h-full overflow-y-auto overflow-x-hidden scroll pl-2" >
                    {chats.map((chat, index) => (
                        <>
                            <div key={index} className="flex flex-row justify-between w-full">
                                {chat.sender === "user" && <div className="min-w-10" />}
                                <div className={`p-4 bg-gray-800 border max-w-full w-max text-wrap border-yellow-500 rounded-lg animate-in-up`}>
                                    <p className="text-yellow-300" dangerouslySetInnerHTML={{ __html: Marked.parse(chat.message) }}/>
                                    <p className={cn("text-yellow-300 w-full text-sm opacity-65 mt-1", chat.sender === "bot" ? "text-left" : "text-right")}>{chat.sender === "bot" ? "Bot" : "You"} {chat.timestamp}</p>
                                </div>
                                {chat.sender !== "user" && <div className="min-w-10" />}
                            </div>
                            {chat.img && chat.img !== "" && <div className="w-full flex flex-row justify-center"><img src={chat.img} alt="img" className="w-64 h-64 my-2 border border-yellow-500 rounded-lg" /></div>}
                        </>
                    ))}

                    {isResponding && <div className="flex flex-row justify-between">
                        <div className="p-4 bg-gray-800 border border-yellow-500 rounded-lg animate-pulse">
                            <p className="text-yellow-300">...</p>
                        </div>
                        <div className="min-w-10" />
                    </div>}

                </div>
            </div>}

            <div className="flex mb-4 w-full max-w-xl">
                <form onSubmit={(e) => { e.preventDefault(); handleDetect(); }} className="flex mb-4 w-full max-w-xl items-center">
                    <input
                        type="text"
                        placeholder="Enter Query"
                        disabled={isResponding}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        className="flex-grow px-4 py-2 border-2 border-yellow-300 rounded-l-lg outline-none bg-gray-800 text-white placeholder-yellow-400"
                    />
                    <Button disabled={isResponding} className="px-4 py-2 bg-yellow-500 border-l border-yellow-600 rounded-r-lg hover:bg-yellow-600 transition-colors ml-2 h-full">
                        DETECT
                    </Button>
                </form>
            </div>
        </div>
    );
};

export default Home;
