
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import './App.css'
import Homepage from './Home'
import Signup from './Signup'
import Prompt from './Prompt'
import Login from './Login'

function App() {


  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Homepage />}></Route>
          <Route path='/signup' element={<Signup />}></Route>
          <Route path='/login' element={<Login />}></Route>
          <Route path='/prompt' element={<Prompt />}></Route>
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
