import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Homepage = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-black text-white relative overflow-hidden">
            {/* Grid Background Pattern */}
            <div className="absolute inset-0 bg-grid-pattern opacity-20"></div>

            {/* Gradient Glow Effect at Bottom */}
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-200 h-100 bg-gradient-radial from-gray-600/30 to-transparent blur-3xl"></div>

            {/* Navigation Bar */}
            <nav className="relative z-10 flex items-center justify-between px-8 py-6">
                <div className="cursor-pointer flex items-center space-x-2">
                    <div className="w-6 h-6 border-2 border-white rotate-45"></div>
                    <span className="text-xl font-semibold ml-1.5">SCINEX</span>
                </div>

                {/* Desktop Menu */}
                <div className="hidden md:flex space-x-8">
                    <a href="#home" className="hover:text-gray-300 transition">Home</a>
                    <a href="#features" className="hover:text-gray-300 transition">Features</a>
                    <a href="#pricing" className="hover:text-gray-300 transition">Pricing</a>
                    <a href="#about" className="hover:text-gray-300 transition">About US</a>
                </div>

                {/* Desktop Launch Button */}
                <button
                    onClick={() => navigate('/signup')}
                    className="cursor-pointer hidden md:block bg-white text-black px-9 py-2 rounded-full font-medium hover:bg-gray-200 transition"
                >
                    SIGN UP
                </button>

                {/* Mobile Hamburger Button */}
                <button
                    className="md:hidden z-50 relative w-10 h-10 flex flex-col items-center justify-center"
                    onClick={() => setIsMenuOpen(!isMenuOpen)}
                    aria-label="Toggle menu"
                >
                    <div className="w-6 h-5 relative flex flex-col justify-between">
                        <span
                            className={`block w-full h-0.5 bg-white transition-all duration-300 origin-center ${isMenuOpen ? 'rotate-45 translate-y-2.25' : ''
                                }`}
                        ></span>
                        <span
                            className={`block w-full h-0.5 bg-white transition-all duration-300 ${isMenuOpen ? 'opacity-0 scale-0' : 'opacity-100 scale-100'
                                }`}
                        ></span>
                        <span
                            className={`block w-full h-0.5 bg-white transition-all duration-300 origin-center ${isMenuOpen ? '-rotate-45 -translate-y-2.25' : ''
                                }`}
                        ></span>
                    </div>
                </button>
            </nav>

            {/* Mobile Menu Overlay */}
            <div
                className={`fixed inset-0 bg-black/95 backdrop-blur-lg z-40 md:hidden transition-all duration-300 ${isMenuOpen ? 'opacity-100 visible' : 'opacity-0 invisible'
                    }`}
            >
                <div className="flex flex-col items-center justify-center h-full space-y-8">
                    <a
                        href="#home"
                        className="text-2xl hover:text-gray-300 transition"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        Home
                    </a>
                    <a
                        href="#features"
                        className="text-2xl hover:text-gray-300 transition"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        Features
                    </a>
                    <a
                        href="#pricing"
                        className="text-2xl hover:text-gray-300 transition"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        Pricing
                    </a>
                    <a
                        href="#about"
                        className="text-2xl hover:text-gray-300 transition"
                        onClick={() => setIsMenuOpen(false)}
                    >
                        About US
                    </a>
                    <button
                        className="cursor-pointer bg-white text-black px-8 py-3 rounded-full font-medium hover:bg-gray-200 transition mt-4"
                        onClick={() => {
                            setIsMenuOpen(false);
                            navigate('/signup');
                        }}
                    >
                        SIGN UP
                    </button>
                </div>
            </div>

            {/* Hero Section */}
            <main className="relative z-10 flex flex-col items-center justify-center px-4 pt-20 pb-32">
                {/* Badge */}
                <div className="mb-8 inline-flex items-center space-x-2 border border-gray-700 rounded-full px-4 py-2 text-sm">
                    <span className="text-white">✦</span>
                    <span>AI-Powered Learning Platform for Science for Technology</span>
                </div>

                {/* Main Heading */}
                <h1 className=" cursor-pointer text-5xl md:text-7xl font-bold text-center max-w-4xl leading-tight mb-6">
                    SCINEX <span className="text-gray-400">Not Just Answers  Understanding.</span>
                </h1>

                {/* Subheading */}
                <p className="text-gray-400 text-center max-w-2xl mb-10 text-lg">
                    SCINEX is an AI-powered learning platform for Science for Technology that adapts to each student’s thinking style. Learn concepts deeply, write your own answers, and get intelligent feedback that helps you truly understand—not just memorize.
                </p>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row gap-4 mb-16">
                    <button
                        onClick={() => navigate('/prompt')}
                        className="cursor-pointer bg-white text-black px-9 py-3 rounded-full font-medium hover:bg-gray-200 transition"
                    >
                        Get Started
                    </button>
                    <button className=" cursor-pointer border border-gray-700 text-white px-9 py-3 rounded-full font-medium hover:bg-gray-900 transition">
                        Learn More
                    </button>
                </div>



            </main>

            {/* Curved Glow Element at Bottom */}
            <div className="absolute bottom-0 left-0 right-0 w-full h-64 overflow-hidden pointer-events-none">
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[90%] h-48">
                    {/* Main curved glow */}
                    <div className="absolute inset-0 bg-linear-to-t from-gray-500/20 via-gray-600/30 to-transparent blur-6xl rounded-t-[90%]"></div>
                    {/* Additional highlight on top edge */}
                    <div className="absolute top-6 left-0 right-0 h-4 bg-linear-to-r from-transparent via-gray-400/40 to-transparent blur-xs"></div>
                </div>
            </div>
        </div>
    );
};

export default Homepage;