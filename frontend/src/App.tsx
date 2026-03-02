import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import LoginPage from './LoginPage'
import Dashboard from './Dashboard'

function AppRoutes(){
  const navigate = useNavigate()

  const handleLogin = () => {
    navigate('/dashboard')
  }

  return(
    <Routes>
      <Route path="/" element={<LoginPage onLogin={handleLogin}/>}/>
      <Route path="/dashboard" element={<Dashboard/>}/>
    </Routes>
  )
}

function App(){
  return(
    <BrowserRouter>
      <AppRoutes/>
    </BrowserRouter>
  )
}


export default App