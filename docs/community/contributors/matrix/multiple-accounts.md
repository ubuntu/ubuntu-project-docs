(matrix-multiple-accounts)=
# Using multiple Matrix accounts

The Element client does not support logging in with multiple concurrent accounts.
However, the same result can be achieved indirectly, as outlined below.


## Using the Element Desktop app

1. **Install Element Desktop:**

   Install via [snap](https://snapcraft.io/element-desktop) or [deb package](https://element.io/download).

1. **Login with your first account:**

   Start Element Desktop and log in with your first account.
   This becomes the default login.

1. **Open a second account:**

   Open a console by pressing {kbd}`Ctrl` + {kbd}`Alt` + {kbd}`T`.

   Run `element-desktop --profile <second-account>` -- this opens Element with your second account.
   If you don't specify your second account, it defaults to the first account.

You can manually start Element with the second account via the CLI, or you can create a Desktop launcher shortcut for it (instructions will vary depending on the Desktop environment you use).


## Using Firefox and Element Web

Firefox has a handy feature called ["Multi Account Containers"](https://addons.mozilla.org/en-US/firefox/addon/multi-account-containers/).
Each container acts as a completely different browser with different accounts.
If you open Element Web in two different containers, you can log into two accounts at the same time.


## Mobile

On mobile, the options are somewhat limited.
While you can use Element Mobile alongside apps like [SchildiChat](https://schildi.chat/) or [FluffyChat](https://fluffychat.im/), they may not fully support all the features used by the Ubuntu Community, potentially impacting your experience.
This will become better with time.

