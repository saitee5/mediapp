import React, { useState}  from 'react';
import { Eye, EyeOff, Shield, Lock } from 'lucide-react';
import assets from '../../assets/assets'

const Login = ({onLogin}) => {
  const[Email, setEmail] = useState('dr.vance@medical.com');
  const [password, setPassword] = useState('password123');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      onLogin({
         name: 'Dr. Julian Vance',
        specialty: 'Cardiology Specialist',
        Email: Email,
        avatar: 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&q=80&w=150',
        onDuty: true
      });
    }, 800);
  };
return(
  <div className='min-h-screen flex font-sans bg-slate-100'>
    {/*left*/}
   <div className='hidden lg:flex lg:w-[45%] bg-linear-to-b from-[#347d7b] via-[#3ca9a5] to-[#13545e] p-12 flex-col justify-between text-white relative overflow-hidden select-none'>
     <div className='absolute top-[-10%] right-[-10%] w-125 h-125 rounded-full bg-teal-500/10 blur-3xl pointer-events-none'></div>
     <div className="absolute bottom-[-10%] left-[-10%] w-125 h-125 rounded-full bg-sky-500/10 blur-3xl pointer-events-none"></div>
    
      {/*header*/}
      <div className="flex items-center gap-2.5 z-10">
         <div className="flex items-center gap-1 bg-white/2 rounded-xl backdrop-blur-md">
    
            <img 
              src={assets.Background} 
              alt="logo" 
              className="w-15- h-15 object-contain"
              />
         
            <span className="font-bold  text-4xl tracking-tight leading-tighht">
              Ambient Clinical Scribe
            </span>
           </div>
        </div>

        {/*picture*/}
        <div className="my-auto max-w-xs mx-auto z-10 flex flex-col items-center">
         
          <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-xl shadow-2xl w-full mb-4 transform hover:scale-[1.02] transition-transform duration-500">
          <img 
           src={assets.patientdoc}
           alt="clinical cons img"
           className="w-full aspect-square object-cover rounded-2xl  bg-linear-to-br from-teal-900/30 to-slate-900/30 border border-white/5 shadow-inner mx-auto blur-[1px]"
           ></img>
           </div>
          
          <div className="text-center">
            <h2 className="text-3xl font-bold font-display tracking-tight leading-tight mb-2">
              AI Powered Clinical Documentation
            </h2>
            <p className="text-sm text-teal-100/80 leading-relaxed font-light">
              Reduce burnout with Ambient Intelligence that understands the nuance of every patient encounter.
            </p>
          </div>

         </div>
        
        <div className="flex items-center gap-6 text-xs text-teal-200/60 z-10 font-medium">
          <span className="flex items-center gap-1.5">
            <Shield className="w-4 h-4 text-teal-400" />
            HIPAA Compliant
          </span>
          <span className="w-1 h-1 bg-teal-500 rounded-full"></span>
          <span className="flex items-center gap-1.5">
            <Lock className="w-4 h-4 text-teal-400" />
            Enterprise Encryption
          </span>
        </div>
      
     
     </div>


     {/*right*/}
     <div className='flex-1 flex-flex-col justify-between p-8 sm:p-12 lg:20 bg-white'>
      <div className='hidden sm:block'></div>

      <div className='max-w-sm w-full mx-auto space-y-7'>

       {/* Header */}
          <div className="space-y-2 text-center lg:text-left">
            <h2 className="text-3xl font-extrabold font-display text-slate-900 tracking-tight">
              Welcome back
            </h2>
            <p className="text-sm text-slate-500 font-medium">
              Access your clinical dashboard to review AI scribes.
            </p>

      </div>
         
          <button 
            type="button" 
            onClick={() => onLogin({
              name: 'Dr. Julian Vance',
              specialty: 'Cardiology Specialist',
              email: 'dr.vance@medical-center.com',
              avatar: 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?auto=format&fit=crop&q=80&w=150',
              onDuty: true
            })}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 border border-slate-200 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 transition-colors shadow-sm cursor-pointer"
          >
             <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22c-.62-.62-1.05-1.37-1.39-2.09z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
            </svg>
            Continue with Google
          </button>

          
          <div className="relative flex items-center justify-center py-2">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-100"></div>
            </div>
            <span className="relative px-3 bg-white text-xs font-bold text-slate-400 tracking-widest uppercase">or</span>
          </div>
          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-1.5">
              <label htmlFor="Email" className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                Email Address
              </label>
              <input
                id="Email"
                type="Email"
                required
                value={Email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="dr.vance@medical-center.com"
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 px-4 py-3 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium"
              />
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                  Password
                </label>
                <a href="#forgot" className="text-xs font-semibold text-[#007e7a] hover:underline">
                  Forgot password?
                </a>
              </div>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-50 border border-slate-200 text-slate-800 placeholder-slate-400 pl-4 pr-12 py-3 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all font-medium"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors focus:outline-none cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-black hover:bg-slate-900 text-white font-bold py-3.5 px-4 rounded-xl text-sm transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>
          {/* Sign Up Redirect */}
          <p className="text-center text-sm font-medium text-slate-500">
            Don't have an account?{' '}
            <a href="#request" className="font-semibold text-[#007e7a] hover:underline">
              Request early access
            </a>
          </p>
        </div>
        {/* Footer */}
        <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 font-medium pt-8 mt-8 border-t border-slate-50 gap-2">
          <span>© 2026 Ambient Clinical Scribe</span>
          <div className="flex items-center gap-4">
            <a href="#privacy" className="hover:text-slate-600 transition-colors">Privacy</a>
            <a href="#terms" className="hover:text-slate-600 transition-colors">Terms</a>
          </div>
        </div>
     </div>
   </div>

)

}


export default Login;