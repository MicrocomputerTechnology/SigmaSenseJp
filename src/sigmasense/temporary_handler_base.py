
from abc import ABC, abstractmethod

class BaseHandler(ABC):
    """
    すべての臨時処理ハンドラの基底クラス。
    臨時ハンドラは必ずこのクラスを継承し、executeメソッドを実装する必要がある。
    """
    @abstractmethod
    def execute(self, narrative: dict) -> dict:
        """
        ハンドラの実行ロジック。

        Args:
            narrative: 処理対象の語りオブジェクト。

        Returns:
            処理結果を格納した辞書。
        """
        pass
