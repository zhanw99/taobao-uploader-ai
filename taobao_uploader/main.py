"""程序入口。"""
from .gui import App


def main() -> None:
    """启动桌面程序。"""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
