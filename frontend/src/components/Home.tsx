import { Button } from "@/components/ui/button";
import React, { useState } from "react";

export const Home: React.FC = () => {
    const [query, setQuery] = useState<string>("");
    const [info, setInfo] = useState<string>("");

    const handleDetect = () => {
        setInfo(`Displays response`); // something happens here
    };

    return (
        <div className="flex flex-col justify-start items-center h-screen bg-gradient-to-br from-blue-500 to-purple-600">
            <h1 className="text-center text-5xl font-extrabold mb-6 text-yellow-300 mt-10">SUS DETECTOR</h1>
            <div className="flex mb-4 w-full max-w-xl mt-60">
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
