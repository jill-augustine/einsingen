import { Button } from "@/components/ui/button";
import axios, { type AxiosResponse } from "axios";
import { HouseIcon, LogInIcon, LogOutIcon, MenuIcon, MenuSquareIcon, SettingsIcon } from "lucide-react";
import type { ComponentProps } from "react";
import { Outlet, redirect, useLoaderData, useOutletContext, type LoaderFunctionArgs } from "react-router"
import { getBackendURL } from "@/url";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

axios.defaults.withCredentials = true; // include cookies on requests

export type User = {
  username: string,
  options: {
    is_guest: boolean
  }
}

export const protectedLoader = async () => {
  const backendURL = getBackendURL()
  try {
    const jsonResponse: AxiosResponse<User> = await axios.get(
      `${backendURL}/api/sessions`,
      { withCredentials: true }
    )
    const response = jsonResponse.data
    return response
  } catch {
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

const AuthenticatedUserHeader = ({ username, isGuest, ...props }: ComponentProps<'header'> & {
  username: string | undefined,
  isGuest: boolean,
}) => {
  return <header className="flex flex-row h-16 items-center gap-2 border-b px-4" {...props}>
    <a href="/" className="flex gap-2 items-center-safe">
      <h1 className="text-xl font-medium">Einsingen</h1> <HouseIcon className="stroke-2 hidden sm:block" />
    </a>
    <div className="flex-grow" />
    <div className="flex gap-2 md:gap-4 items-center">
      <div className="flex justify-end items-center-safe gap-2">
        Hello<span className="text-primary font-semibold truncate">{isGuest ? " Guest" : username?.toLocaleUpperCase()}</span>
        <DropdownMenu >
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size='icon' asChild><MenuIcon /></Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="flex flex-col items-end-safe min-w-0.5 bg-white" align="end">
            {/* TODO: Add highlight on hover */}
            <DropdownMenuItem className="hover:bg-black/5">
              <a href="/settings" className="flex gap-2">
                <SettingsIcon className="stroke-2" aria-hidden="true" /><span>Settings</span>
              </a>
            </DropdownMenuItem>
            <DropdownMenuItem className="hover:bg-black/5">
              <a href="/logout" className="flex gap-2">
                <LogOutIcon />Log Out
              </a>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

      </div>

    </div>
  </header>;
}

export const ProtectedLayout = () => {
  const user = useLoaderData<typeof protectedLoader>()
  return <div className="w-full items-center justify-center p-2 md:p-4 min-w-sm">
    <AuthenticatedUserHeader username={user.username} isGuest={user.options.is_guest} />
    <Outlet context={{ user }} />
  </div>
}

// `useUser` not `getUser` so the function is recognised as React hook
export const useUser = () => {
  return useOutletContext<{ user: User }>()
}
