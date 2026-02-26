import './LoginPage.css'

type Props = {
  onLogin: () => void
}

function LoginPage({ onLogin }: Props){
  return(
    <div className='login-container'>
      <div className='login-content'>
        <div className='logo-section'>
          <h1>BetesBot 0.1</h1>
          <p>Welcome back. Continue to your dashboard</p>
        </div>

        <div className='login-card'>
          <button className='google-btn'>
            Sign in with Google
          </button>

          <div className='divider'>
            <span></span>
            <p>or</p>
            <span></span>
          </div>

          <input type="email" placeholder='Email'/>
          <input type="password" placeholder='Password'/>

          <button
            className='sign-in-btn'
            onClick={onLogin}
          >
            Sign in
          </button>

        </div>

      </div>
    </div>
  )
}

export default LoginPage