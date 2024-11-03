import { Button } from "@/components/ui/button";
import React, { useState, useEffect } from "react";

type Chat = {
    sender: string;
    message: string;
};

export const Home: React.FC = () => {
    const [query, setQuery] = useState<string>("");
    // const [info, setInfo] = useState<string>("");
    const [chats, setChats] = useState<Chat[]>([]);
    const [imageSrc, setImageSrc] = useState<string>("");

    const pushChat = (sender: string, message: string) => {
        setChats((prev) => [...prev, { sender, message }]);
    };

    const handleDetect = () => {
        // setInfo(`${query}`); // something happens here
        pushChat("user", query);
        setQuery("");

        fetch("http://localhost:8000/question", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ query }),
        })
            .then((res) => res.json())
            .then((data) => {
                pushChat("bot", data.message);
            })
            .catch((err) => {
                console.error(err);
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
                <img
                    src={imageSrc}
                    alt="Live Stream"
                    className="w-full h-full object-cover rounded-lg"
                />
            </div>
            <div className="flex mb-4 w-full max-w-xl">
                <form onSubmit={(e) => { e.preventDefault(); handleDetect(); }} className="flex mb-4 w-full max-w-xl items-center">
                    <input
                        type="text"
                        placeholder="Enter Query"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        className="flex-grow px-4 py-2 border-2 border-yellow-300 rounded-l-lg outline-none bg-gray-800 text-white placeholder-yellow-400"
                    />
                    <Button className="px-4 py-2 bg-yellow-500 border-l border-yellow-600 rounded-r-lg hover:bg-yellow-600 transition-colors ml-2 h-full">
                        DETECT
                    </Button>
                </form>
            </div>
            {/* {info != "" && <div className="p-4 bg-gray-800 border border-yellow-500 rounded-lg mt-4">
                <p className="text-yellow-300">{info}</p>
            </div>} */}
            {chats.length > 0 && <div className="gap-1 flex flex-col w-full h-full overflow-auto scroll max-w-xl mt-4 mb-4">
                {chats.map((chat, index) => (
                    <div key={index} className="flex flex-row w-full">
                        {chat.sender === "user" && <div className="w-full" />}
                        <div className={`p-4 bg-gray-800 flex-grow border w-max min-w-max border-yellow-500 rounded-lg animate-in-up ${chat.sender === "bot" ? "ml-auto" : ""}`}>
                            <p className="text-yellow-300">{chat.message}</p>
                        </div>
                    </div>
                ))}
            </div>}
        </div>
    );
};

export default Home;
