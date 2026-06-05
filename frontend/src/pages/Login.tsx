import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogIn, Loader2, ShieldCheck } from 'lucide-react'
import { useAuth } from '../store/auth'

const DEMOS = [
  { nome: 'Diretor', email: 'diretor@trk.com', cor: '#171717' },
  { nome: 'Financeiro', email: 'financeiro@trk.com', cor: '#10b981' },
  { nome: 'RH', email: 'rh@trk.com', cor: '#f59e0b' },
  { nome: 'Comercial', email: 'comercial@trk.com', cor: '#3f3f46' },
]

export function Login() {
  const { entrar } = useAuth()
  const nav = useNavigate()
  const [email, setEmail] = useState('diretor@trk.com')
  const [senha, setSenha] = useState('Trk@123')
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  const submit = async (e?: React.FormEvent) => {
    e?.preventDefault()
    setErro(''); setCarregando(true)
    try { await entrar(email, senha); nav('/') }
    catch { setErro('E-mail ou senha inválidos') }
    finally { setCarregando(false) }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Lado visual */}
      <div className="hidden lg:flex flex-col justify-between p-12 bg-neutral-900 text-white relative overflow-hidden">
        <div className="absolute -top-24 -right-24 w-96 h-96 rounded-full bg-white/5 blur-2xl" />
        <div className="absolute bottom-0 -left-24 w-96 h-96 rounded-full bg-emerald-500/10 blur-2xl" />
        <div className="flex items-center gap-3 relative">
          <div className="w-10 h-10 rounded-xl bg-white text-neutral-900 grid place-items-center font-bold">T</div>
          <span className="font-bold text-lg">TRK OS</span>
        </div>
        <div className="relative">
          <h1 className="text-4xl font-bold leading-tight tracking-tight">O sistema operacional<br />do Grupo TRK.</h1>
          <p className="mt-4 text-white/60 max-w-md">Um universo para a empresa inteira — cada setor com seu acesso, o gestor no controle, e tudo conectado.</p>
          <div className="mt-8 flex items-center gap-2 text-sm text-white/70">
            <ShieldCheck className="w-4 h-4 text-emerald-400" /> Acesso por setor, bloqueio de informação no servidor.
          </div>
        </div>
        <p className="text-xs text-white/40 relative">© {new Date().getFullYear()} Grupo TRK</p>
      </div>

      {/* Form */}
      <div className="flex items-center justify-center p-6 bg-neutral-50">
        <div className="w-full max-w-sm">
          <div className="lg:hidden flex items-center gap-2 mb-8 justify-center">
            <div className="w-10 h-10 rounded-xl bg-neutral-900 text-white grid place-items-center font-bold">T</div>
            <span className="font-bold text-lg">TRK OS</span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight">Entrar</h2>
          <p className="text-sm text-neutral-500 mt-1 mb-6">Bem-vindo de volta.</p>

          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="text-xs font-semibold text-neutral-500">E-mail</label>
              <input className="input mt-1" value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>
            <div>
              <label className="text-xs font-semibold text-neutral-500">Senha</label>
              <input type="password" className="input mt-1" value={senha} onChange={(e) => setSenha(e.target.value)} />
            </div>
            {erro && <div className="chip-danger w-full justify-center py-2">{erro}</div>}
            <button type="submit" disabled={carregando} className="btn-primary w-full py-3">
              {carregando ? <Loader2 className="w-4 h-4 animate-spin" /> : <LogIn className="w-4 h-4" />} Entrar
            </button>
          </form>

          <div className="mt-8">
            <p className="text-xs text-neutral-400 text-center mb-3">Entrar como (demo · senha Trk@123)</p>
            <div className="grid grid-cols-2 gap-2">
              {DEMOS.map((d) => (
                <button key={d.email} onClick={() => { setEmail(d.email); setSenha('Trk@123') }}
                  className="card card-hover p-3 flex items-center gap-2 text-left">
                  <span className="w-7 h-7 rounded-full grid place-items-center text-white text-xs font-bold" style={{ background: d.cor }}>{d.nome[0]}</span>
                  <span className="text-sm font-medium">{d.nome}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
