import { Button } from "@/components/ui/button";
import axios, { type AxiosResponse } from "axios";
import { LogInIcon, LogOutIcon, SettingsIcon } from "lucide-react";
import type { ComponentProps } from "react";
import { Outlet, redirect, useLoaderData, type LoaderFunctionArgs } from "react-router"
import { getBackendURL } from "@/url";

axios.defaults.withCredentials = true; // include cookies on requests

export const protectedLoader = async ({ request }: LoaderFunctionArgs) => {
  const url = new URL(request.url)
  if (url.searchParams.get("isGuestUser")) {
    return { username: undefined, isGuestUser: true }
  }

  const backendURL = getBackendURL()
  try {
    const jsonResponse: AxiosResponse<{ username: string }> = await axios.get(
      `${backendURL}/api/sessions`,
      { withCredentials: true }
    )
    const response: { username: string } = jsonResponse.data
    console.log("Protected page response:", response)
    return { username: response.username, isGuestUser: false }
  } catch {
    console.warn("Protected page error")
    return redirect("/login")
  }
}

const WelcomeCard = ({ username }: { username: string | undefined }) => {
  return (
    <div className="flex justify-end gap-2">
      Hello<span className="text-primary font-semibold">{username ? ` ${username}` : ""}</span>
      <a href="/settings">
        <span className="sr-only">Go to settings</span>
        <SettingsIcon strokeWidth="1" aria-hidden="true" /></a>
    </div>
  )
}
const LogoutButton = ({ ...props }: ComponentProps<'button'>) => {
  return (
    <a href="/logout">
      <Button variant="outline" size="sm" {...props}>
        <LogOutIcon />Log Out
      </Button>
    </a>
  )
}

const LoginButton = ({ ...props }: ComponentProps<'button'>) => {
  return (
    <a href="/login">
      <Button variant="outline" size="sm" {...props}>
        <LogInIcon />Log In
      </Button>
    </a>
  )
}

const AuthenticatedUserHeader = ({ username, ...props }: ComponentProps<'header'> & {
  username: string | undefined,
}) => {
  return <header className="flex flex-row h-16 items-center gap-2 border-b px-4" {...props}>
    <div className="flex gap-2 items-center">
      <h1 className="text-xl font-medium">Einsingen</h1>
    </div>
    <div className="flex-grow" />
    <div className="flex gap-2 md:gap-4 items-center">
      <WelcomeCard username={username} />
      <LogoutButton />
    </div>
  </header>;
}

const GuestUserHeader = ({ ...props }: ComponentProps<'header'> & {
}) => {
  return <header className="flex flex-row h-16 items-center gap-2 border-b px-4" {...props}>
    <div className="flex gap-2 items-center">
      <h1 className="text-xl font-medium">Einsingen</h1>
    </div>
    <div className="flex-grow" />
    <div className="flex gap-2 md:gap-4 items-center">
      <LoginButton />
    </div>
  </header>;
}

export const ProtectedLayout = () => {
  const { username, isGuestUser } = useLoaderData<typeof protectedLoader>()

  return <div className="w-full items-center justify-center p-2 md:p-4 min-w-sm">
    {isGuestUser ? <GuestUserHeader /> : <AuthenticatedUserHeader username={username} />}
    <Outlet />
  </div>
}