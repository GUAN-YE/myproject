using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Data.SqlClient;
using System.Data;

public partial class _Default : System.Web.UI.Page
{

    protected void Page_Load(object sender, EventArgs e)
    {
        if (!IsPostBack)
        {
            dbind();
            bind();
            go();

        }
    }
    public void dbind()
    {
        SqlConnection conn = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123;");
        conn.Open();
        SqlDataAdapter adapter = new SqlDataAdapter("select * from resou ", conn);
        DataTable dt = new DataTable();
        adapter.Fill(dt);
        this.GridView2.DataSource = dt;
        this.GridView2.DataKeyNames = new string[] { "pinpai" };
        this.GridView2.DataBind();
        conn.Close();
    }



    protected void Button2_Click(object sender, EventArgs e)
    {
        Server.Transfer("zhuce.aspx");
    }
    protected void Button3_Click(object sender, EventArgs e)
    {
        Server.Transfer("denglu.aspx");
    }
    protected void GridView2_SelectedIndexChanged(object sender, EventArgs e)
    {

    }
    //protected void ImageButton1_Click(object sender, ImageClickEventArgs e)
    //{
    //    Server.Transfer("sanxing.aspx");
    //}
    //protected void ImageButton2_Click(object sender, ImageClickEventArgs e)
    //{
    //    Server.Transfer("pingguo.aspx");
    //}
    //protected void ImageButton3_Click(object sender, ImageClickEventArgs e)
    //{
    //    Server.Transfer("huawei.aspx");
    //}
    //protected void ImageButton4_Click(object sender, ImageClickEventArgs e)
    //{
    //    Server.Transfer("xiaomi.aspx");
    //}
    //protected void ImageButton11_Click(object sender, ImageClickEventArgs e)
    //{

    //}
    //protected void Button1_Click(object sender, EventArgs e)
    //{
    //    if (DropDownList2.Text == "ipone7")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "ipone6s")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "ipone7")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "iponese")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "w2017")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "note5")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "s7")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "mate9")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "ipone7")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "p9")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "v9")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "MIX")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "note2")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //    else if (DropDownList2.Text == "米5")
    //    {
    //        Server.Transfer("pingguo.aspx");
    //    }
    //}
    //protected void DropDownList1_SelectedIndexChanged(object sender, EventArgs e)
    //{

    //    if (DropDownList1.Text == "苹果")
    //    {
    //        DropDownList2.Items.Clear();
    //        DropDownList2.Items.Add("ipone7");
    //        DropDownList2.Items.Add("ipone6s");
    //        DropDownList2.Items.Add("iponese");
    //    }
    //    if (DropDownList1.Text == "三星")
    //    {
    //        DropDownList2.Items.Clear();
    //        DropDownList2.Items.Add("w2017");
    //        DropDownList2.Items.Add("note5");
    //        DropDownList2.Items.Add("s7");
    //    }
    //    if (DropDownList1.Text == "华为")
    //    {
    //        DropDownList2.Items.Clear();
    //        DropDownList2.Items.Add("mate9");
    //        DropDownList2.Items.Add("p9");
    //        DropDownList2.Items.Add("v9");
    //    }
    //    if (DropDownList1.Text == "小米")
    //    {
    //        DropDownList2.Items.Clear();
    //        DropDownList2.Items.Add("MIX");
    //        DropDownList2.Items.Add("note2");
    //        DropDownList2.Items.Add("米5");
    //    }
    //}

    protected void DropDownList2_SelectedIndexChanged(object sender, EventArgs e)
    {

    }

    public void bind()
    {
        SqlConnection conn = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123;");
        conn.Open();
        SqlDataAdapter adapter = new SqlDataAdapter("select * from tupian1 ", conn);
        DataTable dt = new DataTable();
        adapter.Fill(dt);
        this.DataList1.DataSource = dt;
        this.DataList1.DataKeyField = "tupian";
        this.DataBind();
        conn.Close();
    }
    protected void ImageButton5_Click(object sender, ImageClickEventArgs e)
    {

    }
    public void go()
    {
        SqlConnection conn = new SqlConnection("server=.;database=keti;uid=liubin;pwd=123;");
        conn.Open();
        SqlDataAdapter adapter = new SqlDataAdapter("select * from biaozhi ", conn);
        DataTable dt = new DataTable();
        adapter.Fill(dt);
        this.GridView4.DataSource = dt;
        this.GridView4.DataKeyNames = new string[] { "biaozhi" };
        this.GridView4.DataBind();
        conn.Close();
    }
    protected void GridView4_SelectedIndexChanged(object sender, EventArgs e)
    {

    }
    protected void LinkButton1_Click(object sender, EventArgs e)
    {
        //Server.Transfer("xiangqing.aspx");
    }
    protected void GridView4_SelectedIndexChanged1(object sender, EventArgs e)
    {

    }
    protected void Button5_Click(object sender, EventArgs e)
    {
        Server.Transfer("xiangqing.aspx");
    }



    protected void DropDownList1_SelectedIndexChanged(object sender, EventArgs e)
    {

    }
    protected void Button6_Click(object sender, EventArgs e)
    {
        if (DropDownList1.Text == "三星")
        {
            Server.Transfer("sanxing.aspx");
        }
        else if (DropDownList1.Text == "苹果")
        {
            Server.Transfer("pingguo.aspx");
        }
        else if (DropDownList1.Text == "华为")
        {
            Server.Transfer("~/huawei.aspx");
        }
        else if (DropDownList1.Text == "小米")
        {
            Server.Transfer("xiaomi.aspx");
        }
    }
}