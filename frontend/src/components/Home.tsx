import { Button } from "@/components/ui/button";
import React, { useState, useEffect } from "react";

export const Home: React.FC = () => {
    const [query, setQuery] = useState<string>("");
    const [info, setInfo] = useState<string>("");
    const [imageSrc, setImageSrc] = useState<string>("");

    const handleDetect = () => {
        setInfo(`${query}`); // something happens here
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
        <div className="flex flex-col justify-start items-center h-screen bg-gradient-to-br from-blue-500 to-purple-600">
            <h1 className="text-center text-5xl font-extrabold mb-6 text-yellow-300 mt-10">SUS DETECTOR</h1>

            <div className="w-full max-w-xl h-80 mb-2">
                <img
                    src={imageSrc}
                    alt="Live Stream"
                    className="w-full h-full object-cover rounded-lg"
                />
            </div>
            <div className="flex mb-4 w-full max-w-xl">
                <input
                    type="text"
                    placeholder="Enter Query"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="flex-grow px-4 py-2 border-2 border-yellow-300 rounded-l-lg outline-none bg-gray-800 text-white placeholder-yellow-400"
                />
                <Button onClick={handleDetect} className="px-4 py-2 bg-yellow-500 border-l border-yellow-600 rounded-r-lg hover:bg-yellow-600 transition-colors ml-2">
                    DETECT
                </Button>
            </div>
            <div className="p-4 bg-gray-800 border border-yellow-500 rounded-lg mt-4">
                <p className="text-yellow-300">{info}</p>
            </div>
        </div>
    );
};

export default Home;
