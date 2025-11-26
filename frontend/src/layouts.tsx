import {Button} from "@/components/ui/button";
import axios, {type AxiosResponse} from "axios";
import {LogOutIcon, SettingsIcon} from "lucide-react";
import type {ComponentProps} from "react";
import {Outlet, redirect, useLoaderData} from "react-router"

axios.defaults.withCredentials = true; // include cookies on requests

export const protectedLoader = async () => {
  const url = import.meta.env.BACKEND_URL ?? "http://localhost:8000"
  console.log(url)
  try {
    const jsonResponse: AxiosResponse<{ username: string }> = await axios.get(
      `${url}/api/users/me`,
      {withCredentials: true}
    )
    const response: { username: string } = jsonResponse.data
    console.log("Protected page response:", response)
    return {username: response.username}
  } catch (e) {
    console.warn("Protected page error")
    return redirect("/login")
  }
}

const WelcomeCard = ({username}: { username: string | undefined }) => {
  return (
    <div className="flex justify-end gap-2">
      Hello<span className="text-primary font-semibold">{username ? ` ${username}` : ""}</span>
      <a href="/settings">
        <span className="sr-only">Go to settings</span>
        <SettingsIcon strokeWidth="1" aria-hidden="true"/></a>
    </div>
  )
}
const Logout = ({className}: { className: string }) => {
  return (
    <a href="/logout">
      <Button variant="outline" size="sm" className={className}>
        <LogOutIcon/>Log Out
      </Button>
    </a>
  )
}

const SiteHeader = ({username, ...props}: ComponentProps<'header'> & { username: string | undefined }) => {
  return <header className="flex flex-row h-16 items-center gap-2 border-b px-4" {...props}>
    <div className="flex gap-2 items-center">
      <h1 className="text-xl font-medium">Einsingen</h1>
    </div>
    <div className="flex-grow"/>
    <div className="flex gap-2 md:gap-4 items-center">
      <WelcomeCard username={username}/>
      <Logout className=""/>
    </div>
  </header>;
}

export const ProtectedLayout = () => {
  const {username} = useLoaderData<typeof protectedLoader>()

  return <div className="w-full items-center justify-center p-2 md:p-4 min-w-sm">
    <SiteHeader username={username}/>
    <Outlet/>
  </div>
}