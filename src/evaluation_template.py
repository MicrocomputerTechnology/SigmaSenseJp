from dimension_loader import DimensionLoader
from collections import defaultdict

def display_result(result, dimension_loader: DimensionLoader):
    """
    照合結果を、DimensionLoaderから取得した定義に基づいて動的に表示する。
    """
    image_path = result.get('image_path', 'N/A')
    print(f"\n--- Displaying result for {image_path} ---")

    vector = result.get('vector')
    if not vector:
        print("  No vector found in the result.")
        return

    dimensions = dimension_loader.get_dimensions()
    if len(vector) != len(dimensions):
        print(f"  Warning: Vector length ({len(vector)}) does not match number of dimensions ({len(dimensions)}).")
        return

    # グループごとに結果をまとめる
    grouped_results = defaultdict(list)
    for i, value in enumerate(vector):
        # 0以外の値を持つ次元のみを表示対象とする
        if value != 0:
            dim_info = dimensions[i]
            group = dim_info.get('group', 'Other')
            grouped_results[group].append(f"    - {dim_info.get('name', dim_info['id'])}: {value:.4f} ({dim_info.get('description', 'N/A')})")

    # グループごとに出力
    if not grouped_results:
        print("  All vector values are zero.")
        return
        
    for group, items in sorted(grouped_results.items()):
        print(f"  [{group}]")
        for item in items:
            print(item)