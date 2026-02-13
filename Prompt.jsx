import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Prompt = () => {
    const navigate = useNavigate();
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [inputMessage, setInputMessage] = useState('');

    // Sample chat history
    const chatHistory = [
        'AI-powered Learning Platform',
        'Learning React Effectively',
        'Modern Smooth Navbar Design',
        'අනුරාධපුර අතීත ඉතිහාසය',
        'Login page description',
        'Login page prompt creation',
        'Most famous computer lang...',
        'Vite import error fix',
        'Generate prompt request',
        'Photo background edit',
        'MERN car rental clone'
    ];



    const handleSendMessage = (e) => {
        e.preventDefault();
        if (inputMessage.trim()) {
            // Handle message sending logic here
            console.log('Message sent:', inputMessage);
            setInputMessage('');
        }
    };

    return (
        <div className="flex h-screen bg-[#0d0d0d] text-white overflow-hidden">
            {/* Sidebar */}
            <div
                className={`${isSidebarOpen ? 'w-64' : 'w-0'
                    } bg-[#171717] transition-all duration-300 flex flex-col border-r border-gray-800 overflow-hidden`}
            >
                {/* Sidebar Header */}
                <div className="p-4 border-b border-gray-800">
                    <button
                        onClick={() => navigate('/')}
                        className=" cursor-pointer flex items-center space-x-2 text-gray-400 hover:text-white transition"
                    >
                        <div className="w-6 h-6 border-2 border-white rotate-45"></div>
                        <span className="font-semibold ml-1.5">SCINEX</span>
                    </button>
                </div>

                {/* Sidebar Menu */}
                <div className="flex-1 overflow-y-auto py-4">
                    {/* Main Actions */}
                    <div className="px-3 space-y-2 mb-6">
                        <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg hover:bg-gray-800 transition text-left">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            <span>New chat</span>
                        </button>
                        <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg hover:bg-gray-800 transition text-left">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                            <span>Search chats</span>
                        </button>
                        <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg hover:bg-gray-800 transition text-left">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            <span>Images</span>
                        </button>
                        <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg hover:bg-gray-800 transition text-left">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                            </svg>
                            <span>Apps</span>
                        </button>
                        <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg hover:bg-gray-800 transition text-left">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                            </svg>
                            <span>Codex</span>
                        </button>
                        <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg hover:bg-gray-800 transition text-left">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                            </svg>
                            <span>Projects</span>
                        </button>
                    </div>

                    {/* GPTs Section */}
                    <div className="px-3 mb-4">
                        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-3">
                            SCINEXs
                        </h3>
                        <div className="space-y-1">
                            <button className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition text-left text-sm">
                                <div className="w-6 h-6 bg-linear-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-xs">
                                    R
                                </div>
                                <span className="truncate">Resume AI Website Builder</span>
                            </button>
                            <button className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-800 transition text-left text-sm">
                                <div className="w-6 h-6 bg-linear-to-br from-green-500 to-teal-600 rounded-full flex items-center justify-center text-xs">
                                    E
                                </div>
                                <span className="truncate">Explore SCINEXs</span>
                            </button>
                        </div>
                    </div>

                    {/* Your Chats Section */}
                    <div className="px-3">
                        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-3">
                            Your chats
                        </h3>
                        <div className="space-y-1">
                            {chatHistory.map((chat, index) => (
                                <button
                                    key={index}
                                    className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-800 transition text-left text-sm group"
                                >
                                    <span className="truncate text-gray-300">{chat}</span>
                                    <svg className="w-4 h-4 text-gray-500 opacity-0 group-hover:opacity-100 transition" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" />
                                    </svg>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Sidebar Footer */}
                <div className="p-3 border-t border-gray-800">
                    <button className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-800 transition">
                        <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-linear-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-sm font-semibold">
                                M
                            </div>
                            <div className="text-left">
                                <div className="text-sm font-medium">Malan Chandi...</div>
                                <div className="text-xs text-gray-500">Free</div>
                            </div>
                        </div>
                        <button className="px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded text-xs font-medium transition">
                            Upgrade
                        </button>
                    </button>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col">
                {/* Top Bar */}
                <div className="h-14 border-b border-gray-800 flex items-center justify-between px-4">
                    <div className="flex items-center space-x-4">
                        <button
                            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                            className="p-2 hover:bg-gray-800 rounded-lg transition"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        </button>
                        <button className="flex items-center space-x-2 px-3 py-1.5 rounded-lg hover:bg-gray-800 transition">
                            <span className="font-medium">SCINEX</span>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                    </div>
                    <div className="flex items-center space-x-2">
                        <button className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg transition font-medium">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            <span>Get Plus</span>
                        </button>
                        <button className="p-2 hover:bg-gray-800 rounded-lg transition">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                        </button>
                        <button className="p-2 hover:bg-gray-800 rounded-lg transition">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Chat Area */}
                <div className="flex-1 overflow-y-auto flex flex-col items-center justify-center px-4">
                    <div className="max-w-3xl w-full text-center">
                        <h1 className="text-4xl font-semibold mb-12">What can I help with?</h1>

                        {/* Input Area */}
                        <form onSubmit={handleSendMessage} className="mb-8">
                            <div className="relative">
                                <div className="flex items-center bg-[#2f2f2f] rounded-3xl border border-gray-700 focus-within:border-gray-600 transition">
                                    <button
                                        type="button"
                                        className="p-3 hover:bg-gray-700 rounded-full transition ml-2"
                                    >
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                        </svg>
                                    </button>
                                    <input
                                        type="text"
                                        value={inputMessage}
                                        onChange={(e) => setInputMessage(e.target.value)}
                                        placeholder="Ask anything"
                                        className="flex-1 bg-transparent px-4 py-3 outline-none text-white placeholder-gray-500"
                                    />
                                    <div className="flex items-center space-x-2 pr-2">
                                        <button
                                            type="button"
                                            className="p-2 hover:bg-gray-700 rounded-full transition"
                                        >
                                            <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 24 24">
                                                <circle cx="12" cy="12" r="10" />
                                            </svg>
                                        </button>
                                        <button
                                            type="button"
                                            className="p-2 hover:bg-gray-700 rounded-full transition"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                                            </svg>
                                        </button>
                                        <button
                                            type="button"
                                            className="p-2 hover:bg-gray-700 rounded-full transition"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </form>


                    </div>
                </div>
            </div>
        </div>
    );
};

export default Prompt;