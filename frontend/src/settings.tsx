import axios, { AxiosError, type AxiosResponse } from "axios";
import { useState } from "react";
import { type ActionFunctionArgs, Link, useFetcher, useLoaderData } from 'react-router'
import * as z from "zod";

import { Button } from '@/components/ui/button'
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { type User, protectedLoader, useUser } from '@/layouts'
import { getBackendURL } from '@/url';
import { BanIcon, ChevronDown, ChevronRight } from "lucide-react";
import { Separator } from "@/components/ui/separator";

type ResponseSuccess = { user: User, error: never }
type ParsingError = { error: string, user: never }
type ResponseError = ParsingError


const action = async ({ request }: ActionFunctionArgs): Promise<ResponseSuccess | ResponseError> => {

    const updatePasswordFormSchema = z.object({
        username: z.string(),
        currentPassword: z.string(),
        newPassword: z.string(),
    })

    const formData = await request.formData()
    const { data: parsedFormData, error: parsingError } = updatePasswordFormSchema.safeParse({
        username: formData.get('username'),
        currentPassword: formData.get('current-password'),
        newPassword: formData.get('new-password'),
    })
    if (parsingError) {
        return { error: "Submitted values could not be parsed correctly." } as ParsingError
    }

    const url = getBackendURL()
    // 1) Change password
    try {
        const resp: AxiosResponse<{ detail: string }> = await axios.put(
            `${url}/api/users/${parsedFormData.username}/password`,
            JSON.stringify({
                current_password: parsedFormData.currentPassword,
                new_password: parsedFormData.newPassword,
            }),
            { headers: { "Content-Type": "application/json" } }
        )
        console.log(resp)
    } catch (e) {
        const axiosError = e as AxiosError<{ detail: string }>
        return {
            error: axiosError.response?.data.detail || 'An error occurred',
        } as ResponseError
    }
    // 2) Get new session using new password (otherwise user is directed to /login page after password update)
    try {
        const resp2: AxiosResponse<User> = await axios.post(
            `${url}/api/sessions`,
            JSON.stringify(
                {
                    username: parsedFormData.username,
                    password: parsedFormData.newPassword,
                }
            ),
            { headers: { "Content-Type": "application/json" } }
        )
        return { user: resp2.data } as ResponseSuccess
    } catch {
        return {
            error: 'An error occurred',
        } as ResponseError
    }
}
type UpdatePasswordProps = {
    fetcher: ReturnType<typeof useFetcher>,
    state: "submitting" | "success" | "ready",
    error?: string,
    user?: User,
}

export const UpdateSettingsCard = ({ fetcher, state, error, user }: UpdatePasswordProps) => {

    const [isCollapsible1Open, setIsCollapsible1Open] = useState<boolean>(true)
    const formFields: { label: ReturnType<typeof Label>, input: ReturnType<typeof Input> }[] = [
        {
            label: <Label htmlFor="username">Username</Label>,
            input: <Input id="username" name="username" type="text" value={user?.username} readOnly className="text-gray-500" />
        },
        {
            label: <Label htmlFor="password">Current Password</Label>,
            input: <Input id="current-password" name="current-password" type="password" required />
        },
        {
            label: <Label htmlFor="new-password">New Password</Label>,
            input: <Input id="new-password" name="new-password" type="password" required />
        }
    ]

    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-2xl">Settings</CardTitle>
            </CardHeader>
            {user?.options.is_guest ?
                <CardContent className="flex flex-row wrap gap-2">
                    <BanIcon className="flex shrink-0 mr-4" />
                    <div className="flex flex-col">Guest users cannot update app preferences.<span><Link to="/sign-up" className="underline underline-offset-4 pt-4">
                        Sign up
                    </Link> to update app preferences.</span></div>
                </CardContent> :
                <Collapsible asChild open={isCollapsible1Open} onOpenChange={setIsCollapsible1Open}>
                    <CardContent>
                        <CollapsibleTrigger className="flex flex-row w-full pb-6">
                            <span className="text-left">Update your password</span><span id="spacer" className="grow" />{isCollapsible1Open ? <ChevronDown className="flex-none" /> : <ChevronRight className="flex-none" />}
                        </CollapsibleTrigger>
                        <CollapsibleContent asChild>
                            <fetcher.Form method="post" className="flex flex-col gap-6">
                                {formFields.map((field, i) => <div className="grid gap-2" key={i}>
                                    {field.label}
                                    {field.input}
                                </div>)}
                                {error && <p className="text-sm text-red-500">{error}</p>}
                                {state === "success" && <p className="text-sm">Password updated successfully!</p>}
                                <Button type="submit" variant="outline" className="self-center-safe w-50" disabled={state === "submitting"}>
                                    {state === "submitting" ? 'Updating...' : 'Update Password'}
                                </Button>
                            </fetcher.Form>
                        </CollapsibleContent>
                        {/* Activate this once there is another section for preferences */}
                        {/* <Separator className="bg-black/10 my-3" /> */}
                    </CardContent>
                </Collapsible>
            }
        </Card >
    )
}

const Component = () => {
    const { user } = useUser()
    const fetcher = useFetcher<typeof action>()
    const error = fetcher.data?.error
    const state = fetcher.state === 'submitting' ? fetcher.state : (fetcher.data?.user ? 'success' : 'ready')
    return (
        // items-start so toggling collapsibles doesn't cause page to jump
        <div className="flex min-h-svh w-full items-start justify-center p-6 md:p-10">
            <div className="w-full max-w-sm">
                <div className="flex flex-col gap-6">
                    <UpdateSettingsCard fetcher={fetcher} error={error} state={state} user={user} />
                </div>
            </div>
        </div>)
}

export const route = {
    path: 'settings',
    Component,
    action,
}